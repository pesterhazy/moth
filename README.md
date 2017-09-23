## Synopsis

`moth` is a simple package manager.

- Uses content-addressable storage
- Allows private dependencies
- Works cross-platform (Linux/macOS)
- Requires no dependencies

Expect more here soon

## Usage

To add moth to a new project, simply download the current `moth` binary to your project directory:

```
$ mkdir myproject
$ cd myproject
$ bash -c 'curl -fsSLo moth https://github.com/pesterhazy/moth/releases/download/r${1}/moth && chmod +x moth' -- a62d2a621be13d88741234bf5ac51fabb56f911c
# ./moth version
```

## Author

Paulus Esterhazy <pesterhazy@gmail.com>
