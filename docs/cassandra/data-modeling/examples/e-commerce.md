# E-Commerce Data Model Example

E-commerce has all the interesting data modeling challenges: products that need to be queried multiple ways, shopping carts that get abandoned, orders that move through states, inventory that needs to stay consistent. It is a good exercise for thinking through Cassandra's query-first approach.

The core tension is always denormalization vs. consistency. A product appears in the catalog, in a cart, in an order, in inventory counts—and these must stay in sync without transactions. Cassandra provides patterns for this: TTLs for cart cleanup, lightweight transactions for inventory reservation, separate tables for different query patterns.

This example works through a complete e-commerce schema, showing the reasoning behind each table design.

## Business Requirements

### Core Functionality

An e-commerce platform requires:

- **Product Catalog** - Browse products, search, filter by category
- **User Accounts** - Registration, authentication, profiles
- **Shopping Cart** - Temporary cart storage, item management
- **Order Processing** - Checkout, order history, status tracking
- **Inventory Management** - Stock levels, availability checks
- **Analytics** - Sales metrics, product popularity

### Query Requirements

Before designing tables, list every query the application needs:

```
Product Queries:
─────────────────────────────────────────────────────────────────
Q1:  Get product details by product_id
Q2:  List products in a category (paginated, sortable)
Q3:  Search products by name prefix
Q4:  Get featured/popular products for homepage
Q5:  Get related products

User Queries:
─────────────────────────────────────────────────────────────────
Q6:  Get user profile by user_id
Q7:  Authenticate user by email (login)
Q8:  Get user's saved addresses

Shopping Cart Queries:
─────────────────────────────────────────────────────────────────
Q9:  Get all items in user's cart
Q10: Check if specific product is in cart

Order Queries:
─────────────────────────────────────────────────────────────────
Q11: Get user's order history (recent first)
Q12: Get order details by order_id
Q13: Get items in a specific order
Q14: Get order status history
Q15: Get orders by status (for admin dashboard)

Inventory Queries:
─────────────────────────────────────────────────────────────────
Q16: Check product inventory across warehouses
Q17: Reserve inventory (with consistency guarantee)

Analytics Queries:
─────────────────────────────────────────────────────────────────
Q18: Get daily sales by category
Q19: Get top products by views
```

---

## Schema Design

### User-Defined Types

First, define reusable types for complex structures:

```sql
-- Address type (used in users and orders)
CREATE TYPE address (
    label TEXT,           -- 'home', 'work', 'shipping'
    street TEXT,
    street2 TEXT,
    city TEXT,
    state TEXT,
    postal_code TEXT,
    country TEXT,
    phone TEXT
);

-- Price type (for internationalization)
CREATE TYPE price (
    amount DECIMAL,
    currency TEXT         -- 'USD', 'EUR', etc.
);

-- Product summary (for denormalization)
CREATE TYPE product_summary (
    product_id UUID,
    name TEXT,
    image_url TEXT,
    price DECIMAL
);
```

---

## Product Catalog

### Products by ID (Q1)

The primary product table for detailed product views:

```sql
CREATE TABLE products (
    product_id UUID,
    name TEXT,
    slug TEXT,                              -- URL-friendly name
    description TEXT,
    category_id UUID,
    category_name TEXT,                     -- Denormalized for display
    brand TEXT,
    price DECIMAL,
    compare_at_price DECIMAL,               -- Original price for sales
    currency TEXT,
    sku TEXT,
    weight_grams INT,
    dimensions MAP<TEXT, INT>,              -- height, width, depth in mm
    image_urls LIST<TEXT>,
    thumbnail_url TEXT,
    attributes MAP<TEXT, TEXT>,             -- color: 'blue', size: 'large'
    tags SET<TEXT>,
    status TEXT,                            -- 'active', 'draft', 'archived'
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    PRIMARY KEY ((product_id))
);

-- Query: Get full product details
SELECT * FROM products WHERE product_id = ?;
```

**Design notes:**
- Single partition per product for fast point lookups
- Collections kept small (< 50 items each)
- Category name denormalized to avoid join

### Products by Category (Q2)

For browsing products within a category:

```sql
CREATE TABLE products_by_category (
    category_id UUID,
    sort_key TEXT,                          -- Composite: 'price_asc:00000599:prod-uuid'
    product_id UUID,
    name TEXT,
    thumbnail_url TEXT,
    price DECIMAL,
    compare_at_price DECIMAL,
    rating_average DECIMAL,
    rating_count INT,
    in_stock BOOLEAN,
    PRIMARY KEY ((category_id), sort_key, product_id)
);

-- Query: Get products in category, sorted by price
SELECT * FROM products_by_category
WHERE category_id = ?
LIMIT 24;

-- Query: Pagination (next page)
SELECT * FROM products_by_category
WHERE category_id = ?
  AND sort_key > ?
LIMIT 24;
```

**Sort key construction:**

```python
def build_sort_key(sort_type: str, value: any, product_id: str) -> str:
    """
    Build composite sort key for deterministic ordering.

    sort_type: 'price_asc', 'price_desc', 'name_asc', 'newest', 'popular'
    """
    if sort_type == 'price_asc':
        # Pad price to 10 digits for proper string sorting
        return f"price_asc:{value:010.2f}:{product_id}"
    elif sort_type == 'price_desc':
        # Invert for descending (max_price - actual_price)
        inverted = 9999999.99 - float(value)
        return f"price_desc:{inverted:010.2f}:{product_id}"
    elif sort_type == 'newest':
        # Invert timestamp for descending
        inverted = 9999999999 - int(value.timestamp())
        return f"newest:{inverted:010d}:{product_id}"
    # ... etc
```

**Why this approach:**
- Enables efficient pagination without OFFSET
- Supports multiple sort orders in same table
- Product ID ensures uniqueness

### Products by Name Prefix (Q3)

For search-as-you-type functionality:

```sql
CREATE TABLE products_by_name_prefix (
    name_prefix TEXT,                       -- First 2-3 characters
    name_lower TEXT,                        -- Lowercase full name
    product_id UUID,
    name TEXT,
    thumbnail_url TEXT,
    price DECIMAL,
    category_name TEXT,
    PRIMARY KEY ((name_prefix), name_lower, product_id)
);

-- Query: Search for "iph*"
SELECT * FROM products_by_name_prefix
WHERE name_prefix = 'iph'
LIMIT 10;
```

**Insertion (application code):**

```python
def index_product_for_search(session, product):
    """Index product for prefix search."""
    name_lower = product['name'].lower()

    # Index first 2 and 3 character prefixes
    prefixes = [name_lower[:2], name_lower[:3]]

    for prefix in prefixes:
        session.execute(insert_stmt, [
            prefix,
            name_lower,
            product['product_id'],
            product['name'],
            product['thumbnail_url'],
            product['price'],
            product['category_name']
        ])
```

**Note:** For production search, consider Elasticsearch or Cassandra SAI.

### Featured Products (Q4)

For homepage display:

```sql
CREATE TABLE featured_products (
    feature_type TEXT,                      -- 'homepage', 'deals', 'new_arrivals'
    position INT,
    product_id UUID,
    name TEXT,
    thumbnail_url TEXT,
    price DECIMAL,
    compare_at_price DECIMAL,
    badge TEXT,                             -- 'Sale', 'New', 'Bestseller'
    PRIMARY KEY ((feature_type), position)
);

-- Query: Get homepage featured products
SELECT * FROM featured_products
WHERE feature_type = 'homepage'
LIMIT 12;
```

---

## User Management

### Users by ID (Q6)

Primary user profile table:

```sql
CREATE TABLE users (
    user_id UUID,
    email TEXT,
    password_hash TEXT,
    first_name TEXT,
    last_name TEXT,
    phone TEXT,
    avatar_url TEXT,
    default_address_id UUID,
    addresses LIST<FROZEN<address>>,        -- Max ~5 addresses
    preferences MAP<TEXT, TEXT>,
    email_verified BOOLEAN,
    status TEXT,                            -- 'active', 'suspended', 'deleted'
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    last_login_at TIMESTAMP,
    PRIMARY KEY ((user_id))
);

-- Query: Get user profile
SELECT * FROM users WHERE user_id = ?;
```

### Users by Email (Q7)

For authentication:

```sql
CREATE TABLE users_by_email (
    email TEXT,
    user_id UUID,
    password_hash TEXT,
    email_verified BOOLEAN,
    status TEXT,
    PRIMARY KEY ((email))
);

-- Query: Login authentication
SELECT user_id, password_hash, email_verified, status
FROM users_by_email
WHERE email = ?;
```

**Authentication flow:**

```python
def authenticate_user(session, email: str, password: str) -> Optional[UUID]:
    """Authenticate user and return user_id if successful."""

    # Step 1: Look up by email
    row = session.execute(
        "SELECT user_id, password_hash, email_verified, status "
        "FROM users_by_email WHERE email = ?",
        [email]
    ).one()

    if not row:
        return None  # User not found

    if row.status != 'active':
        raise AccountDisabledException()

    if not row.email_verified:
        raise EmailNotVerifiedException()

    # Step 2: Verify password
    if not verify_password(password, row.password_hash):
        return None  # Invalid password

    # Step 3: Update last login
    session.execute(
        "UPDATE users SET last_login_at = toTimestamp(now()) WHERE user_id = ?",
        [row.user_id]
    )

    return row.user_id
```

**Maintaining both tables:**

```sql
-- User registration (atomic write to both tables)
BEGIN BATCH
    INSERT INTO users (user_id, email, password_hash, first_name, last_name,
                       email_verified, status, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, false, 'active', toTimestamp(now()), toTimestamp(now()));

    INSERT INTO users_by_email (email, user_id, password_hash, email_verified, status)
    VALUES (?, ?, ?, false, 'active');
APPLY BATCH;
```

---

## Shopping Cart

### Cart Items (Q9, Q10)

Shopping cart with automatic expiration:

```sql
CREATE TABLE shopping_carts (
    user_id UUID,
    product_id UUID,
    product_name TEXT,
    product_image TEXT,
    unit_price DECIMAL,
    quantity INT,
    selected_options MAP<TEXT, TEXT>,       -- size: 'L', color: 'blue'
    added_at TIMESTAMP,
    PRIMARY KEY ((user_id), product_id)
) WITH default_time_to_live = 2592000       -- 30 days
  AND gc_grace_seconds = 86400;             -- 1 day (with daily repair)

-- Query: Get all cart items
SELECT * FROM shopping_carts WHERE user_id = ?;

-- Query: Get specific item
SELECT * FROM shopping_carts WHERE user_id = ? AND product_id = ?;
```

**Cart operations:**

```sql
-- Add item to cart (upsert)
INSERT INTO shopping_carts (user_id, product_id, product_name, product_image,
                            unit_price, quantity, selected_options, added_at)
VALUES (?, ?, ?, ?, ?, ?, ?, toTimestamp(now()));

-- Update quantity
UPDATE shopping_carts SET quantity = ?, added_at = toTimestamp(now())
WHERE user_id = ? AND product_id = ?;

-- Remove item
DELETE FROM shopping_carts WHERE user_id = ? AND product_id = ?;

-- Clear cart (after checkout)
DELETE FROM shopping_carts WHERE user_id = ?;
```

**Note:** The cart stores a snapshot of product info at add time. This is intentional—users see the price they selected, not current price.

---

## Order Processing

### Orders by User (Q11)

User's order history:

```sql
CREATE TABLE orders_by_user (
    user_id UUID,
    order_date DATE,
    order_id UUID,
    status TEXT,
    total DECIMAL,
    item_count INT,
    first_item_name TEXT,                   -- "iPhone 15 and 2 more items"
    first_item_image TEXT,
    PRIMARY KEY ((user_id), order_date, order_id)
) WITH CLUSTERING ORDER BY (order_date DESC, order_id DESC);

-- Query: Get recent orders
SELECT * FROM orders_by_user
WHERE user_id = ?
LIMIT 20;

-- Query: Orders in date range
SELECT * FROM orders_by_user
WHERE user_id = ?
  AND order_date >= '2024-01-01'
  AND order_date <= '2024-12-31';
```

### Order Details (Q12)

Full order information:

```sql
CREATE TABLE orders (
    order_id UUID,
    order_number TEXT,                      -- Human-readable: 'ORD-2024-123456'
    user_id UUID,
    user_email TEXT,
    status TEXT,

    -- Addresses (snapshot at order time)
    shipping_address FROZEN<address>,
    billing_address FROZEN<address>,

    -- Payment
    payment_method TEXT,
    payment_status TEXT,
    payment_id TEXT,                        -- External payment provider ID

    -- Pricing
    subtotal DECIMAL,
    discount_amount DECIMAL,
    discount_code TEXT,
    shipping_amount DECIMAL,
    tax_amount DECIMAL,
    total DECIMAL,
    currency TEXT,

    -- Shipping
    shipping_method TEXT,
    tracking_number TEXT,
    carrier TEXT,
    estimated_delivery DATE,

    -- Timestamps
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    paid_at TIMESTAMP,
    shipped_at TIMESTAMP,
    delivered_at TIMESTAMP,
    cancelled_at TIMESTAMP,

    -- Notes
    customer_notes TEXT,
    internal_notes TEXT,

    PRIMARY KEY ((order_id))
);

-- Query: Get order details
SELECT * FROM orders WHERE order_id = ?;
```

### Order Items (Q13)

Line items for an order:

```sql
CREATE TABLE order_items (
    order_id UUID,
    line_number INT,
    product_id UUID,
    product_name TEXT,
    product_image TEXT,
    sku TEXT,
    selected_options MAP<TEXT, TEXT>,
    unit_price DECIMAL,
    quantity INT,
    line_total DECIMAL,
    PRIMARY KEY ((order_id), line_number)
);

-- Query: Get all items in order
SELECT * FROM order_items WHERE order_id = ?;
```

### Order Status History (Q14)

Track status changes:

```sql
CREATE TABLE order_status_history (
    order_id UUID,
    status_time TIMESTAMP,
    status TEXT,
    actor TEXT,                             -- 'system', 'admin:john', 'customer'
    notes TEXT,
    PRIMARY KEY ((order_id), status_time)
) WITH CLUSTERING ORDER BY (status_time DESC);

-- Query: Get status history
SELECT * FROM order_status_history WHERE order_id = ?;
```

### Orders by Status (Q15)

For admin dashboard:

```sql
CREATE TABLE orders_by_status (
    status TEXT,
    order_date DATE,
    order_id UUID,
    order_number TEXT,
    user_email TEXT,
    total DECIMAL,
    created_at TIMESTAMP,
    PRIMARY KEY ((status, order_date), created_at, order_id)
) WITH CLUSTERING ORDER BY (created_at DESC, order_id DESC)
  AND default_time_to_live = 2592000;       -- 30 days retention

-- Query: Get pending orders for today
SELECT * FROM orders_by_status
WHERE status = 'pending' AND order_date = toDate(now())
LIMIT 50;
```

**Note:** Partition by (status, date) to prevent unbounded growth.

---

## Order Creation Flow

Creating an order involves multiple tables. Here is the complete flow:

```sql
-- Step 1: Validate cart and calculate totals (read operations)
SELECT * FROM shopping_carts WHERE user_id = ?;

-- Step 2: Reserve inventory for each item (with LWT)
UPDATE inventory
SET reserved = reserved + ?
WHERE product_id = ? AND warehouse_id = ?
IF reserved + ? <= quantity;
-- Check [applied] = true before proceeding

-- Step 3: Create order (atomic batch)
BEGIN BATCH
    -- Main order record
    INSERT INTO orders (order_id, order_number, user_id, user_email, status,
                        shipping_address, billing_address, payment_method,
                        subtotal, discount_amount, shipping_amount, tax_amount, total,
                        currency, created_at, updated_at)
    VALUES (?, ?, ?, ?, 'pending', ?, ?, ?, ?, ?, ?, ?, ?, 'USD',
            toTimestamp(now()), toTimestamp(now()));

    -- Order items (repeat for each item)
    INSERT INTO order_items (order_id, line_number, product_id, product_name,
                            product_image, sku, selected_options, unit_price,
                            quantity, line_total)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);

    -- User's order history
    INSERT INTO orders_by_user (user_id, order_date, order_id, status, total,
                               item_count, first_item_name, first_item_image)
    VALUES (?, toDate(now()), ?, 'pending', ?, ?, ?, ?);

    -- Status history
    INSERT INTO order_status_history (order_id, status_time, status, actor, notes)
    VALUES (?, toTimestamp(now()), 'pending', 'system', 'Order created');

    -- Admin dashboard
    INSERT INTO orders_by_status (status, order_date, order_id, order_number,
                                  user_email, total, created_at)
    VALUES ('pending', toDate(now()), ?, ?, ?, ?, toTimestamp(now()));

    -- Clear cart
    DELETE FROM shopping_carts WHERE user_id = ?;
APPLY BATCH;
```

### Status Update Flow

```python
def update_order_status(session, order_id: UUID, user_id: UUID,
                        old_status: str, new_status: str, actor: str, notes: str):
    """Update order status across all relevant tables."""

    now = datetime.utcnow()
    today = now.date()

    # Get order details for denormalized updates
    order = session.execute(
        "SELECT order_number, user_email, total FROM orders WHERE order_id = ?",
        [order_id]
    ).one()

    # Atomic status update
    batch = BatchStatement()

    # Update main order
    batch.add(
        session.prepare("UPDATE orders SET status = ?, updated_at = ? WHERE order_id = ?"),
        [new_status, now, order_id]
    )

    # Add to status history
    batch.add(
        session.prepare("""
            INSERT INTO order_status_history (order_id, status_time, status, actor, notes)
            VALUES (?, ?, ?, ?, ?)
        """),
        [order_id, now, new_status, actor, notes]
    )

    # Update user's order list
    batch.add(
        session.prepare("""
            UPDATE orders_by_user SET status = ?
            WHERE user_id = ? AND order_date = ? AND order_id = ?
        """),
        [new_status, user_id, today, order_id]
    )

    # Remove from old status partition, add to new
    batch.add(
        session.prepare("""
            DELETE FROM orders_by_status
            WHERE status = ? AND order_date = ? AND created_at = ? AND order_id = ?
        """),
        [old_status, today, order.created_at, order_id]
    )
    batch.add(
        session.prepare("""
            INSERT INTO orders_by_status (status, order_date, order_id, order_number,
                                          user_email, total, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """),
        [new_status, today, order_id, order.order_number, order.user_email,
         order.total, order.created_at]
    )

    session.execute(batch)
```

---

## Inventory Management

### Inventory Table (Q16)

```sql
CREATE TABLE inventory (
    product_id UUID,
    warehouse_id TEXT,
    quantity INT,
    reserved INT,
    low_stock_threshold INT,
    updated_at TIMESTAMP,
    PRIMARY KEY ((product_id), warehouse_id)
);

-- Query: Check inventory across warehouses
SELECT * FROM inventory WHERE product_id = ?;
```

### Inventory Reservation (Q17)

Use lightweight transactions for consistency:

```sql
-- Reserve inventory (optimistic)
UPDATE inventory
SET reserved = reserved + ?,
    updated_at = toTimestamp(now())
WHERE product_id = ? AND warehouse_id = ?
IF reserved + ? <= quantity;

-- Response: [applied] = true/false
-- If false: insufficient inventory

-- Release reservation (on order cancel or timeout)
UPDATE inventory
SET reserved = reserved - ?
WHERE product_id = ? AND warehouse_id = ?;

-- Confirm order (reduce actual quantity)
UPDATE inventory
SET quantity = quantity - ?,
    reserved = reserved - ?
WHERE product_id = ? AND warehouse_id = ?;
```

**Inventory reservation pattern:**

```python
class InventoryService:
    def reserve_items(self, items: List[dict]) -> bool:
        """Reserve inventory for all items. Returns True if all succeed."""

        reserved = []

        try:
            for item in items:
                # Try to reserve each item
                result = self.session.execute(reserve_stmt, [
                    item['quantity'],
                    item['product_id'],
                    item['warehouse_id'],
                    item['quantity']
                ]).one()

                if not result.applied:
                    # Insufficient inventory - rollback
                    self._release_reservations(reserved)
                    return False

                reserved.append(item)

            return True

        except Exception as e:
            # Error - rollback any successful reservations
            self._release_reservations(reserved)
            raise

    def _release_reservations(self, items: List[dict]):
        """Release previously made reservations."""
        for item in items:
            self.session.execute(release_stmt, [
                item['quantity'],
                item['product_id'],
                item['warehouse_id']
            ])
```

---

## Analytics Tables

### Daily Sales (Q18)

```sql
CREATE TABLE daily_sales (
    date DATE,
    category_id UUID,
    order_count COUNTER,
    item_count COUNTER,
    revenue_cents COUNTER                   -- Store as cents for counter precision
);

-- Update on order completion
UPDATE daily_sales SET
    order_count = order_count + 1,
    item_count = item_count + ?,
    revenue_cents = revenue_cents + ?
WHERE date = toDate(now()) AND category_id = ?;

-- Query: Today's sales by category
SELECT * FROM daily_sales WHERE date = toDate(now());
```

### Product Views (Q19)

```sql
CREATE TABLE product_views (
    product_id UUID,
    date DATE,
    view_count COUNTER,
    unique_visitor_count COUNTER,
    PRIMARY KEY ((product_id), date)
) WITH default_time_to_live = 7776000;      -- 90 days

-- Track view
UPDATE product_views SET view_count = view_count + 1
WHERE product_id = ? AND date = toDate(now());

-- Query: Views over last 7 days
SELECT * FROM product_views
WHERE product_id = ?
  AND date >= '2024-01-08'
  AND date <= '2024-01-15';
```

---

## Complete Schema Summary

```sql
-- Types
CREATE TYPE address (...);
CREATE TYPE price (...);
CREATE TYPE product_summary (...);

-- Product tables
CREATE TABLE products (...);                     -- Q1: By product_id
CREATE TABLE products_by_category (...);         -- Q2: Browse category
CREATE TABLE products_by_name_prefix (...);      -- Q3: Search
CREATE TABLE featured_products (...);            -- Q4: Homepage

-- User tables
CREATE TABLE users (...);                        -- Q6: By user_id
CREATE TABLE users_by_email (...);               -- Q7: Login

-- Cart tables
CREATE TABLE shopping_carts (...);               -- Q9, Q10: Cart items

-- Order tables
CREATE TABLE orders_by_user (...);               -- Q11: User history
CREATE TABLE orders (...);                       -- Q12: Order details
CREATE TABLE order_items (...);                  -- Q13: Line items
CREATE TABLE order_status_history (...);         -- Q14: Status tracking
CREATE TABLE orders_by_status (...);             -- Q15: Admin dashboard

-- Inventory tables
CREATE TABLE inventory (...);                    -- Q16, Q17: Stock

-- Analytics tables
CREATE TABLE daily_sales (...);                  -- Q18: Sales metrics
CREATE TABLE product_views (...);                -- Q19: Popularity
```

---

## Consistency Levels

| Operation | Consistency | Reason |
|-----------|-------------|--------|
| Read product | LOCAL_ONE | Can tolerate slightly stale |
| Read user profile | LOCAL_QUORUM | User expects current data |
| Login authentication | LOCAL_QUORUM | Security-critical |
| Read cart | LOCAL_QUORUM | Session-critical |
| Update cart | LOCAL_QUORUM | Must not lose items |
| Reserve inventory | QUORUM + LWT | Must be consistent |
| Create order | QUORUM | Financial transaction |
| Read order history | LOCAL_QUORUM | User expects current status |
| Update order status | QUORUM | Must not lose updates |
| Analytics counters | ANY/ONE | Approximate is acceptable |

---

## Production Considerations

### Write Amplification

| Entity | Tables Updated | Writes per Operation |
|--------|----------------|---------------------|
| New product | products, products_by_category, products_by_name_prefix | 3+ |
| User registration | users, users_by_email | 2 |
| Add to cart | shopping_carts | 1 |
| Create order | 6+ tables | 6+ |
| Update status | orders, order_status_history, orders_by_user, orders_by_status | 4 |

### Partition Size Monitoring

```bash
# Tables likely to have large partitions
nodetool tablehistograms ecommerce.orders_by_user    # Power users
nodetool tablehistograms ecommerce.products_by_category  # Popular categories
nodetool tablehistograms ecommerce.shopping_carts    # Abandoned carts
```

### TTL Strategy

| Table | TTL | Reason |
|-------|-----|--------|
| shopping_carts | 30 days | Clean up abandoned carts |
| order_status_history | None | Permanent audit trail |
| orders_by_status | 30 days | Only need recent for dashboard |
| product_views | 90 days | Historical analytics limit |
| daily_sales | None | Permanent business metrics |

---

## Next Steps

- **[Time Bucketing](../patterns/time-bucketing.md)** - For high-volume events
- **[Anti-Patterns](../anti-patterns/index.md)** - Mistakes to avoid
- **[Operations Guide](../../operations/index.md)** - Production operations
- **[Performance Tuning](../../operations/performance/index.md)** - Optimization
