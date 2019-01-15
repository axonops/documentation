
# Getting started

## Installation

### Installing AxonOps Server

Before installing [AxonOps Server][1], you need to make sure you have ... and ... – ... up and running. You can verify if you're already good to go with the following commands:

``` sh
.. --version
# ... 2.7.13
... --version
# ... 9.0.1
```

Installing and verifying AxonOps Server is as simple as:

``` sh
apt-get install axonops && axonops --version
# axonops, version 0.17.1
```

AxonOps Server requires Agent >= 0.17.1.

  [1]: https://axonops.com

### Installing Agent

#### using apt-get

Agent can be installed with `apt-get`:

``` sh
apt-get install java-agent
```

#### using other methods

you're on Windows you can use [Link][2] to install [Method][3]:

``` dos
apt-get install axonops-server
```

This will install all required dependencies like [something][4] and [something else][5].

  [2]: https://#
  [3]: https://#
  [4]: https://#
  [5]: https://#

#### cloning from GitHub

AxonOps Server can also be used without a system-wide installation by cloning the repository into a subfolder of your project's root directory:

``` sh
git clone https://github.com/squidfunk/axonops.git
```

This is especially useful if you want to extend the app and
override some parts of the app. The app will reside in the folder
`path-to/folder`.

 

### Troubleshooting

!!! warning "Installation on macOS"

    When you're running the pre-installed version of Python on macOS,, `axonops`
    tries to install packages in a folder for which your user might not have the adequate permissions. There are two possible solutions for this:

    1. **Installing in user space** (recommended): Provide the `--user` flag
      to the install command and `axonops` will install the package in a user-site
      location. This is the recommended way.

    2. **Switching to a homebrewed Python**: Upgrade your Python installation
      to a self-contained solution by installing Python with Homebrew. This
      should eliminate a lot of problems you may be having with `axonops`.

!!! failure "Error: unrecognized theme 'axonops'"

    If you run into this error, the most common reason is that you installed
     AxonOps Server through some package manager (e.g. Homebrew or `apt-get`) and the
    Material theme through `pip`, so both packages end up in different
    locations. AxonOps only checks its install location for themes.

### Alternative: Using Docker

If you're familiar with Docker, the official [Docker image][8] for Material
comes with all dependencies pre-installed and ready-to-use with the latest
version published on PyPI, packaged in a very small image. Pull it with:

```
docker pull squidfunk/mkdocs-material
```

The `axonops` executable is provided as an entrypoint, `serve` is the default
command. Start the development server in your project root with:

```
docker run --rm -it -p 8000:8000 -v ${PWD}:/docs squidfunk/mkdocs-material
```

If you're using Windows command prompt (`cmd.exe`), substitute `${PWD}` with
`"%cd%"`.

  [8]: https://hub.docker.com/r/squidfunk/mkdocs-material/

## Usage

In order to run axonops server just add one of the following lines to your
project's `config.yml`. If you installed Axonops using a package manager:

``` yaml
MQTT:
  endpoints: ""
RESTConfig:
  host: 0.0.0.0 
  port: 8080
  elastic_host: localhost
  elastic_port: 9200
alerting:
  notification_interval: 3h
  notification_endpoints:
  axonops_host: "http://localhost:3000/"
  axonops_logo: "https://digitalis.io/wp-content/uploads/2018/11/slack_axonops.png"
  axonops_website: "https://www.axonops.com/"
backup:
    localRetentionDurationDays: 30
```



Axonops server  includes a development server, so you can review your changes as you go.
The development server can be started with the following command:

``` sh
./axonops 
```

Now you can point your browser to [http://localhost:3000][9] and the Material
theme should be visible. From here on, you can start writing your documentation,
or read on and customize the theme.

  [9]: http://localhost:3000

## Configuration

### Color palette

A default hue is defined for every primary and accent color on Google's
Material Design [color palette][10], which makes it very easy to change the
overall look of the theme. Just set the primary and accent colors using the
following variables:

``` yaml
theme:
  palette:
    primary: 'indigo'
    accent: 'indigo'
```





