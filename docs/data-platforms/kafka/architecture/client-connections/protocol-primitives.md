---
title: "Kafka Protocol Primitive Types"
description: "Apache Kafka wire protocol primitive data types. Integer encoding, variable-length integers, strings, bytes, arrays, and tagged fields."
meta:
  - name: keywords
    content: "Kafka protocol primitives, data types, varint, compact arrays, tagged fields"
---

# Kafka Protocol Primitive Types

This document specifies the primitive data types used in the Apache Kafka binary wire protocol. All multi-byte values use big-endian (network) byte order unless otherwise specified. Implementations must encode and decode these types exactly as specified.

---

## Integer Types

### Fixed-Width Signed Integers

| Type | Size | Range | Encoding |
|------|:----:|-------|----------|
| `INT8` | 1 byte | -128 to 127 | Two's complement, big-endian |
| `INT16` | 2 bytes | -32,768 to 32,767 | Two's complement, big-endian |
| `INT32` | 4 bytes | -2,147,483,648 to 2,147,483,647 | Two's complement, big-endian |
| `INT64` | 8 bytes | -9,223,372,036,854,775,808 to 9,223,372,036,854,775,807 | Two's complement, big-endian |

**Encoding Examples:**

| Value | Type | Bytes (hex) |
|------:|------|-------------|
| 0 | INT8 | `00` |
| -1 | INT8 | `FF` |
| 127 | INT8 | `7F` |
| -128 | INT8 | `80` |
| 256 | INT16 | `01 00` |
| -1 | INT16 | `FF FF` |
| 16909060 | INT32 | `01 02 03 04` |

### Fixed-Width Unsigned Integers

| Type | Size | Range | Encoding |
|------|:----:|-------|----------|
| `UINT16` | 2 bytes | 0 to 65,535 | Unsigned, big-endian |
| `UINT32` | 4 bytes | 0 to 4,294,967,295 | Unsigned, big-endian |

!!! note "Unsigned Integer Usage"
    Unsigned integers are used sparingly in the protocol. `UINT16` and `UINT32` appear only in specific APIs, while `UNSIGNED_VARINT` is the compact length primitive.

---

## Variable-Length Integers

Variable-length integers provide efficient encoding of small values while supporting the full range of 32-bit or 64-bit integers.

### VARINT (Signed 32-bit)

A variable-length encoded signed 32-bit integer using zig-zag encoding.

| Property | Value |
|----------|-------|
| **Maximum encoded size** | 5 bytes |
| **Value range** | -2,147,483,648 to 2,147,483,647 |
| **Encoding** | Zig-zag + variable-length |

**Zig-zag Transformation:**

```
encoded = (value << 1) ^ (value >> 31)
```

This transformation maps signed values to unsigned values:

| Signed Value | Zig-zag Encoded |
|-------------:|----------------:|
| 0 | 0 |
| -1 | 1 |
| 1 | 2 |
| -2 | 3 |
| 2 | 4 |
| 2147483647 | 4294967294 |
| -2147483648 | 4294967295 |

**Variable-Length Encoding:**

After zig-zag transformation, the value is encoded using continuation bits:

- Each byte uses 7 bits for data and 1 bit (MSB) as continuation flag
- MSB = 1 indicates more bytes follow
- MSB = 0 indicates final byte

```
Byte layout: [C][D6][D5][D4][D3][D2][D1][D0]
  C = Continuation bit (1 = more bytes, 0 = last byte)
  D = Data bits (7 per byte, little-endian order)
```

**Encoding Examples:**

| Value | Zig-zag | Encoded Bytes (hex) |
|------:|--------:|---------------------|
| 0 | 0 | `00` |
| -1 | 1 | `01` |
| 1 | 2 | `02` |
| 63 | 126 | `7E` |
| 64 | 128 | `80 01` |
| -65 | 129 | `81 01` |
| 8191 | 16382 | `FE 7F` |
| 8192 | 16384 | `80 80 01` |

!!! warning "Maximum Byte Length"
    Implementations must reject VARINT values encoded in more than 5 bytes as a protocol error. A valid VARINT must have the continuation bit clear (0) by the 5th byte.

### VARLONG (Signed 64-bit)

A variable-length encoded signed 64-bit integer using zig-zag encoding.

| Property | Value |
|----------|-------|
| **Maximum encoded size** | 10 bytes |
| **Value range** | -9,223,372,036,854,775,808 to 9,223,372,036,854,775,807 |
| **Encoding** | Zig-zag + variable-length |

**Zig-zag Transformation:**

```
encoded = (value << 1) ^ (value >> 63)
```

!!! warning "Maximum Byte Length"
    Implementations must reject VARLONG values encoded in more than 10 bytes as a protocol error.

### UNSIGNED_VARINT (Unsigned 32-bit)

A variable-length encoded unsigned 32-bit integer without zig-zag transformation.

| Property | Value |
|----------|-------|
| **Maximum encoded size** | 5 bytes |
| **Value range** | 0 to 4,294,967,295 |
| **Encoding** | Variable-length (no zig-zag) |

**Encoding Examples:**

| Value | Encoded Bytes (hex) |
|------:|---------------------|
| 0 | `00` |
| 1 | `01` |
| 127 | `7F` |
| 128 | `80 01` |
| 16383 | `FF 7F` |
| 16384 | `80 80 01` |

**Primary Usage:**

- Length fields in compact encodings (`COMPACT_STRING`, `COMPACT_ARRAY`, etc.)
- Tagged field metadata
- Flexible version headers

---

## Floating Point

### FLOAT64

A double-precision 64-bit IEEE 754 floating-point number.

| Property | Value |
|----------|-------|
| **Size** | 8 bytes |
| **Encoding** | IEEE 754 binary64, big-endian |
| **Special values** | NaN, +Infinity, -Infinity supported |

**Byte Layout:**

```
Bit 63:    Sign (0 = positive, 1 = negative)
Bits 62-52: Exponent (11 bits, biased by 1023)
Bits 51-0:  Mantissa (52 bits)
```

!!! note "NaN Handling"
    The Kafka protocol does not mandate a specific NaN payload. When deserializing, any value with exponent bits all set and non-zero mantissa must be interpreted as NaN.

---

## UUID

A universally unique identifier as defined in RFC 4122.

| Property | Value |
|----------|-------|
| **Size** | 16 bytes |
| **Encoding** | Big-endian (most significant bits first) |
| **Zero UUID** | 16 zero bytes (sentinel in some APIs) |

**Byte Layout:**

```
Bytes 0-7:  Most significant 64 bits (time_low, time_mid, time_hi_and_version)
Bytes 8-15: Least significant 64 bits (clock_seq, node)
```

**Zero UUID:**

Some APIs use an all-zero UUID as a sentinel value:

```
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
```

!!! note "UUID Version"
    The Kafka protocol does not mandate a specific UUID version.

---

## Boolean

A single-byte boolean value.

| Property | Value |
|----------|-------|
| **Size** | 1 byte |
| **False** | 0x00 |
| **True** | Any non-zero value |

**Encoding Rules:**

| Requirement | Level |
|-------------|-------|
| Implementations should write 0x00 for false | should |
| Implementations should write 0x01 for true | should |
| Implementations must interpret 0x00 as false | must |
| Implementations must interpret any non-zero value as true | must |

---

## String Types

### STRING (Non-Nullable)

A length-prefixed UTF-8 string that cannot be null.

| Property | Value |
|----------|-------|
| **Length field** | INT16 |
| **Maximum length** | 32,767 bytes |
| **Null handling** | Not nullable |

**Wire Format:**

```
STRING => length:INT16 data:BYTES[length]
```

**Encoding Example:**

| String | Length | Encoded Bytes (hex) |
|--------|:------:|---------------------|
| "" | 0 | `00 00` |
| "a" | 1 | `00 01 61` |
| "hello" | 5 | `00 05 68 65 6C 6C 6F` |

!!! warning "Null Constraint"
    A length value of -1 must be rejected as invalid for non-nullable STRING. Implementations must not encode null values using this type.

### NULLABLE_STRING

A length-prefixed UTF-8 string that may be null.

| Property | Value |
|----------|-------|
| **Length field** | INT16 |
| **Maximum length** | 32,767 bytes |
| **Null indicator** | -1 |

**Wire Format:**

```
NULLABLE_STRING => length:INT16 [data:BYTES[length]]
  If length == -1: null (no data bytes)
  If length >= 0:  exactly 'length' data bytes follow
```

**Encoding Example:**

| String | Length | Encoded Bytes (hex) |
|--------|:------:|---------------------|
| null | -1 | `FF FF` |
| "" | 0 | `00 00` |
| "test" | 4 | `00 04 74 65 73 74` |

### COMPACT_STRING (Non-Nullable)

A variable-length prefixed UTF-8 string using compact encoding.

| Property | Value |
|----------|-------|
| **Length field** | UNSIGNED_VARINT |
| **Length semantics** | Actual length + 1 |
| **Maximum length** | 2³²-2 bytes |
| **Null handling** | Not nullable |

**Wire Format:**

```
COMPACT_STRING => length:UNSIGNED_VARINT data:BYTES[length-1]
```

The length field encodes `actual_length + 1`, so:
- Length value 1 = empty string (0 bytes)
- Length value 2 = 1-byte string
- Length value N = (N-1)-byte string

**Encoding Example:**

| String | Wire Length | Encoded Bytes (hex) |
|--------|:-----------:|---------------------|
| "" | 1 | `01` |
| "a" | 2 | `02 61` |
| "hello" | 6 | `06 68 65 6C 6C 6F` |

!!! warning "Null Constraint"
    A length value of 0 must be rejected as invalid for non-nullable COMPACT_STRING.

### COMPACT_NULLABLE_STRING

A variable-length prefixed UTF-8 string using compact encoding that may be null.

| Property | Value |
|----------|-------|
| **Length field** | UNSIGNED_VARINT |
| **Null indicator** | 0 |
| **Maximum length** | 2³²-2 bytes |

**Wire Format:**

```
COMPACT_NULLABLE_STRING => length:UNSIGNED_VARINT [data:BYTES[length-1]]
  If length == 0: null (no data bytes)
  If length > 0:  exactly 'length-1' data bytes follow
```

**Encoding Example:**

| String | Wire Length | Encoded Bytes (hex) |
|--------|:-----------:|---------------------|
| null | 0 | `00` |
| "" | 1 | `01` |
| "test" | 5 | `05 74 65 73 74` |

---

## Bytes Types

### BYTES (Non-Nullable)

A length-prefixed byte array that cannot be null.

| Property | Value |
|----------|-------|
| **Length field** | INT32 |
| **Maximum length** | 2,147,483,647 bytes |
| **Null handling** | Not nullable |

**Wire Format:**

```
BYTES => length:INT32 data:BYTE[length]
```

### NULLABLE_BYTES

A length-prefixed byte array that may be null.

| Property | Value |
|----------|-------|
| **Length field** | INT32 |
| **Maximum length** | 2,147,483,647 bytes |
| **Null indicator** | -1 |

**Wire Format:**

```
NULLABLE_BYTES => length:INT32 [data:BYTE[length]]
  If length == -1: null (no data bytes)
  If length >= 0:  exactly 'length' data bytes follow
```

### COMPACT_BYTES (Non-Nullable)

A variable-length prefixed byte array using compact encoding.

| Property | Value |
|----------|-------|
| **Length field** | UNSIGNED_VARINT |
| **Length semantics** | Actual length + 1 |
| **Maximum length** | 2³²-2 bytes |
| **Null handling** | Not nullable |

**Wire Format:**

```
COMPACT_BYTES => length:UNSIGNED_VARINT data:BYTE[length-1]
```

!!! warning "Null Constraint"
    A length value of 0 must be rejected as invalid for non-nullable COMPACT_BYTES.

### COMPACT_NULLABLE_BYTES

A variable-length prefixed byte array using compact encoding that may be null.

| Property | Value |
|----------|-------|
| **Length field** | UNSIGNED_VARINT |
| **Null indicator** | 0 |
| **Maximum length** | 2³²-2 bytes |

**Wire Format:**

```
COMPACT_NULLABLE_BYTES => length:UNSIGNED_VARINT [data:BYTE[length-1]]
  If length == 0: null (no data bytes)
  If length > 0:  exactly 'length-1' data bytes follow
```

---

## Array Types

### ARRAY

A count-prefixed array of elements that may be null.

| Property | Value |
|----------|-------|
| **Count field** | INT32 |
| **Maximum elements** | 2,147,483,647 |
| **Null indicator** | -1 |

**Wire Format:**

```
ARRAY<T> => count:INT32 [elements:T[count]]
  If count == -1: null array (no elements)
  If count >= 0:  exactly 'count' elements follow
```

!!! note "Empty vs Null"
    An empty array (count = 0) is semantically distinct from a null array (count = -1). Implementations must preserve this distinction.

### COMPACT_ARRAY

A variable-length count-prefixed array using compact encoding.

| Property | Value |
|----------|-------|
| **Count field** | UNSIGNED_VARINT |
| **Count semantics** | Actual count + 1 |
| **Null indicator** | 0 |

**Wire Format:**

```
COMPACT_ARRAY<T> => count:UNSIGNED_VARINT [elements:T[count-1]]
  If count == 0: null array (no elements)
  If count > 0:  exactly 'count-1' elements follow
```

**Count Semantics:**

| Wire Count | Meaning |
|:----------:|---------|
| 0 | Null array |
| 1 | Empty array (0 elements) |
| 2 | Array with 1 element |
| N | Array with N-1 elements |

---

## Records Types

### RECORDS

Message batch data in Kafka record format.

| Property | Value |
|----------|-------|
| **Length field** | INT32 |
| **Null indicator** | -1 |
| **Content** | One or more RecordBatch structures |

**Wire Format:**

```
RECORDS => length:INT32 [data:BYTE[length]]
  If length == -1: null (no record data)
  If length >= 0:  exactly 'length' bytes of record batch data
```

### COMPACT_RECORDS

Message batch data using compact encoding.

| Property | Value |
|----------|-------|
| **Length field** | UNSIGNED_VARINT |
| **Null indicator** | 0 |
| **Content** | One or more RecordBatch structures |

**Wire Format:**

```
COMPACT_RECORDS => length:UNSIGNED_VARINT [data:BYTE[length-1]]
  If length == 0: null (no record data)
  If length > 0:  exactly 'length-1' bytes of record batch data
```

See [Protocol Records](protocol-records.md) for the record batch format specification.

---

## Tagged Fields

Introduced in Kafka 2.4 (KIP-482), tagged fields enable forward-compatible protocol evolution without incrementing API versions.

### Structure

```
TaggedFields => num_fields:UNSIGNED_VARINT [field:TaggedField]*

TaggedField => tag:UNSIGNED_VARINT size:UNSIGNED_VARINT data:BYTES[size]
```

| Field | Type | Description |
|-------|------|-------------|
| `num_fields` | UNSIGNED_VARINT | Number of tagged fields |
| `tag` | UNSIGNED_VARINT | Unique field identifier |
| `size` | UNSIGNED_VARINT | Size of field data in bytes |
| `data` | BYTES | Raw field data |

### Behavioral Requirements

| Requirement | Level | Description |
|-------------|-------|-------------|
| Tag ordering | must | Tagged fields must be serialized in strictly ascending tag order |
| Unknown tags | must | Implementations must ignore (skip) unknown tagged fields |
| Duplicate tags | must | Implementations must reject duplicate tags as a protocol error |
| Tag value range | must | Tag values must be non-negative |

### Version Applicability

Tagged fields are only valid in "flexible" API versions:

| API Version Type | Request Tagged Fields | Response Tagged Fields |
|------------------|:---------------------:|:----------------------:|
| Non-flexible | ❌ | ❌ |
| Flexible | ✅ | ✅ |

!!! note "Flexible Version Detection"
    Each API specifies which versions are "flexible" in its schema. Flexible versions use compact encodings (COMPACT_STRING, COMPACT_ARRAY, etc.) and include tagged field sections.

---

## Type Summary

### Primitive Types

| Type | Size | Nullable | Compact Variant |
|------|:----:|:--------:|:---------------:|
| INT8 | 1 | ❌ | - |
| INT16 | 2 | ❌ | - |
| INT32 | 4 | ❌ | - |
| INT64 | 8 | ❌ | - |
| UINT16 | 2 | ❌ | - |
| UINT32 | 4 | ❌ | - |
| VARINT | 1-5 | ❌ | - |
| VARLONG | 1-10 | ❌ | - |
| UNSIGNED_VARINT | 1-5 | ❌ | - |
| FLOAT64 | 8 | ❌ | - |
| UUID | 16 | ❌ | - |
| BOOLEAN | 1 | ❌ | - |

### Complex Types

| Type | Length Field | Nullable | Compact Variant |
|------|--------------|:--------:|-----------------|
| STRING | INT16 | ❌ | COMPACT_STRING |
| NULLABLE_STRING | INT16 | ✅ | COMPACT_NULLABLE_STRING |
| BYTES | INT32 | ❌ | COMPACT_BYTES |
| NULLABLE_BYTES | INT32 | ✅ | COMPACT_NULLABLE_BYTES |
| ARRAY | INT32 | ✅ | COMPACT_ARRAY |
| RECORDS | INT32 | ✅ | COMPACT_RECORDS |

---

## Implementation Notes

### Byte Order

All multi-byte primitive types use big-endian (network) byte order. This applies to:

- Fixed-width integers (INT16, INT32, INT64, UINT16, UINT32)
- Floating point (FLOAT64)
- UUID

Variable-length integers (VARINT, VARLONG, UNSIGNED_VARINT) use little-endian data bit ordering within their variable-length encoding.

### String Encoding

All string types use UTF-8 encoding. Implementations must:

- Encode strings as valid UTF-8
- Accept and preserve valid UTF-8 sequences
- Handle invalid UTF-8 as implementation-defined (may reject or replace)

### Memory Considerations

| Concern | Recommendation |
|---------|----------------|
| Maximum message size | Validate against configured limits before allocation |
| Array allocation | Check count bounds before allocating arrays |
| String length | Validate length does not exceed available bytes |

---

## Related Documentation

- [Protocol Messages](protocol-messages.md) - Message framing and headers
- [Protocol Records](protocol-records.md) - Record batch format
- [Protocol Errors](protocol-errors.md) - Error code reference
- [Kafka Protocol](kafka-protocol.md) - Protocol overview
