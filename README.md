## Synopsis

`moth` is a simple dependency manager based on the following principles:

- Content-addressable storage: use sha hashes to identify dependencies
- Project-centric: works from your project directory (Git repo)
- Private: allows non-public, authenticated dependencies
- Cross-platform: works on Linux and macOS (with Windows as a possibility)
- Self-contained: requires no dependencies

To keep things simple, the project defines a number of non-goals:

- No transitive dependencies, in contrast to npm, maven etc.
- No integration with git, in contrast to alternatives like [git-annex](https://git-annex.branchable.com/) and [git-lfs](https://git-lfs.github.com/) (although this could be added as a separate project)

## Maturity

Moth is currently in **early development**; expect breaking changes.

## Getting started

Simple installation is one of moth's goals. No global installation is necessary.

To add moth to a new project, simply download the current `moth` binary to your project directory:

```
bash -c 'curl -fsSLo moth https://github.com/pesterhazy/moth/releases/download/r${1}/moth && chmod +x moth' -- 9abfe309e816dc08da39dffa257b4d854a190aac
```

## Tutorial

Start by configuring a repository. The `moth init` command expects a repository URL and creates a fresh `moth.yaml` in the current directory:

```shell
./moth init --repository "file:$HOME/.moth-local"
cat moth.json
```

Upload a dependency:

```shell
echo "Bom dia" > hello.txt
./moth put --input-file hello.txt
```

This writes a file to the `~/.moth-local` folder. Local filesystem-based repositories are not as useful as remote repositories, but they are easier to so we'll use one in this tutorial. The process for uploading to a cloud storage service is similar.

Note that `moth put` prints the SHA hash of the content you just uploaded to the terminal:

```
504b7c6424e6fa94402786315bb58bc1e504bb8f
```

You can use this hash to retrieve the dependency again:

```shell
./moth get --sha 504b7c6424e6fa94402786315bb58bc1e504bb8f
```

or download it to the local cache:

```shell
./moth show --sha 504b7c6424e6fa94402786315bb58bc1e504bb8f
```

You can also show the file contents from the local cache. This will download the file only if it isn't present already:

```shell
./moth show --sha 504b7c6424e6fa94402786315bb58bc1e504bb8f --cat
```

Often, the dependencies you work with contain multiple files. Moth supports this through the concept of a workspace. A workspace is uploaded simply by uploading a zip file:

```shell
mkdir many
echo uno > many/one.txt
echo due > many/two.txt
( cd many && zip -X ../many.zip -r * && stripzip ../many.zip )
./moth put --input-file many.zip
```

The result is the hash `93287c444a1a870de36107c26c569ab28154ca9f`. Again `moth show` can print the path to the downloaded content:

```shell
./moth show --sha 93287c444a1a870de36107c26c569ab28154ca9f
```

But you can also find and access paths to files within the workspace:

```shell
./moth show --sha 93287c444a1a870de36107c26c569ab28154ca9f --find one.txt
```

Which prints:

```
/home/user/.moth/db/db/afe/93287c444a1a870de36107c26c569ab28154ca9f/workspace/one.txt
```

Or

```shell
./moth show --sha 93287c444a1a870de36107c26c569ab28154ca9f --find one.txt --cat
```

which prints:

```
uno
```

When used with the `--find` flag, moth automatically extract zip files in a local folder. This makes it easy to refer to workspace contents from other scripts.

SHA1 hashes are long enough to ensure that hash collisions are unlikely. But they're also difficult to remember, so moth allows you to refer to objects by using aliases. First define the alias:

```shell
./moth alias --alias many --sha 93287c444a1a870de36107c26c569ab28154ca9f
```

This updates `moth.json`. Now you can refer to the object using an alias:

```shell
./moth show --alias many
```

If the aliased object is a zip file, can also refer to files inside the workspace:

```shell
./moth show --alias many --find one.txt --cat
```

## Usage

```
./moth
```

```
usage: moth <command> [args]

Getting started

  init      Initialize moth project in current directory
  version   Print current moth version

Managing data

  put       Put object
  alias     Add or update alias

Retrieving data

  show      Read object
```

## URL types

The following URL types are implemented:

- `s3://` - S3-based repository. As this backend is ased on the [boto](https://github.com/boto/boto3) library, refer to its [documentation](http://boto3.readthedocs.io/en/latest/guide/configuration.html) for how to specify credientials. Credentials can be specified using the `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` environment variables or using the `~/.aws/credentials` configuration file. Example: `s3://mybucket`
- `http://` and `https://` - Read-only repository accessed via HTTP(S). The https backend can be used to access any unauthenticated, world-readable S3 bucket. Example: `https://mybucket.s3.amazonaws.com/`
- `file://` - local file system repository. Mostly for testing `file://home/user/repo`

## License

```
Copyright © 2017 Paulus Esterhazy <pesterhazy@gmail.com>

Distributed under the Eclipse Public License
```
