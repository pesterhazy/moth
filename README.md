## Synopsis

`moth` is a simple package manager. It's based on the following principles:

- Content-addressable storage: use sha hashes to identify dependencies
- Project-centric: works from your project directory (Git repo)
- Private: allows non-public, authenticated dependencies
- Cross-platform: works on Linux and macOS
- Self-contained: requires no dependencies

Expect more here soon

## Getting started

Simple installation is one of moth's goals. No global installation is necessary.

To add moth to a new project, simply download the current `moth` binary to your project directory:

```
$ mkdir myproject
$ cd myproject
$ touch moth.yaml
$ bash -c 'curl -fsSLo moth https://github.com/pesterhazy/moth/releases/download/r${1}/moth && chmod +x moth' -- a62d2a621be13d88741234bf5ac51fabb56f911c
$ ./moth version
```

## Tutorial

Set the repository. Let's use a local file-based repository:

```
export MOTH_REPOSITORY="file:$HOME/.moth-local"
```

Upload a dependency:

```
$ ./moth put --input-file hello.txt
504b7c6424e6fa94402786315bb58bc1e504bb8f
```

This writes a file to the `~/.moth-local` folder, but the process for uploading to a cloud storage service is similar.

Note that this command writes back the SHA hash of the content you uploaded. You can use this hash to retrieve the dependency again:

```
$ ./moth show --sha 504b7c6424e6fa94402786315bb58bc1e504bb8f
/User/asdf/test/.moth/db/db/504/504b7c6424e6fa94402786315bb58bc1e504bb8f/contents
```

You can show the file:

```
$ ./moth show --sha 504b7c6424e6fa94402786315bb58bc1e504bb8f --cat
Bom dia
```

Often, the dependencies you work with contain multiple files. Moth supports this through the concept of a workspace. A workspace is uploaded simply by uploading a zip file:

```
$ mkdir many
$ echo uno > many/one.txt
$ echo due > many/two.txt
$ ( cd many && zip ../many.zip -r * )
  adding: one.txt (stored 0%)
  adding: two.txt (stored 0%)
$ ./moth put --input-file many.zip
a0e1119b1dc49f08d79072c13efc81047024047c
```

Again moth can print the path to the content:

```
$ ./moth show --sha a0e1119b1dc49f08d79072c13efc81047024047c
/Users/asdf/test/.moth/db/db/a0e/a0e1119b1dc49f08d79072c13efc81047024047c/contents
```

But you can also find and access paths to files within the workspace:

```
$ ./moth show --sha a0e1119b1dc49f08d79072c13efc81047024047c --find one.txt
/Users/pe/prg/testmoth/.moth/db/db/a0e/a0e1119b1dc49f08d79072c13efc81047024047c/workspace/one.txt
$ ./moth show --sha a0e1119b1dc49f08d79072c13efc81047024047c --find one.txt --cat
uno
```

When used with the `--find` flag, moth automatically extract zip files in a local folder. This makes it easy to refer to workspace contents from other scripts.

SHA1 hashes are long enough to ensure that hash collisions are unlikely. But they're also difficult to remember, so moth allows you to refer to objects through aliases. First define the alias in `moth.yaml`:

```
cat > moth.yaml <<EOF
aliases:
  many:
    sha: a0e1119b1dc49f08d79072c13efc81047024047c
EOF
```

Now you can refer to the object using an alias:

```
$ ./moth show --alias many
/Users/asdf/testmoth/.moth/db/db/a0e/a0e1119b1dc49f08d79072c13efc81047024047c/contents
```

If the aliased object is a zip file, can also refer to files inside the workspace:

```
$ ./moth show --alias many --find one.txt --cat
uno
```

## Usage

```
$ ./moth
usage: moth <command> [args]

The following commands are available:

  show      Read object
  put       Put object
  version   Print current moth version
```

## Author

Paulus Esterhazy <pesterhazy@gmail.com>
