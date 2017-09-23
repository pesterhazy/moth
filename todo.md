# todo

- clean up main.py
- add backend for http(s)
- set MAIN_SHA in moth.yaml

# old

- add `moth check <dep>` commmand
- make `moth run` check dependency
- add manifest (moth.yaml?) to each dependency's directory
- multi-flle vs single-file dependencies

# Design

- content-addressable storage
- use object-sha as identifier, instead of [artifact-id version]
- different sub-projects:
    - moth-bin
        - bootstrap
        - only knows how to retrieve moth-core, then delegates to moth-core
        - substrate
        - can be committed to repos (compare how gradle does it)
        - changes rarely (if ever)
        - defaults to using PROJECT_ROOT/.moth
    - moth-core
        - contains main CLI
        - version of moth-core is defined explicitly in `moth.yaml`
        - main operations:
            - `moth get <coordinates>`
    - moth-url
        - k/v store provider for URLs. Supports `file://` and `https://` urls
        - no authentication
        - can be used for public repositories
        - can also be used for private repositories if they disallows "List" operations
    - moth-github
        - k/v store provider for Github releases (read only)
        - unclear: how is this an object store?
        - used for plugins?
    - moth-s3
        - k/v store provider for S3 buckets
        - GET and PUT
        - uses awscli under the hood
        - awscli handles authentication
    - moth-gcloud
        - k/v store provider for Google Cloud Storage buckets
        - GET and PUT
        - uses gcloud under the hood
        - glcoud handles authentication
    
- investigate if these tools can be in a single monorepo
- plugins
    - check how other tools do it
        - e.g. vagrant, other hashicorp tools
- coordinate design
    - URIs?

# Concepts

- coordinates:
  - `<provider-spec>:<hash>`
  - `provider-spec` can be an obj-hash or an alias
  - an alias is an obj-hash with optional provider-params
- alias:
    - alternative name for an object. Objects can have multiple aliases, but an alias can only refer to a single object.
    
# Example commands

Get an object using the fully qualified url:

```
$ moth path moth/moth-s3::acme-moth::cafe01

Retrieving...
0%
10%
100%.

Unpacking...

.moth/objects/cafe/cafe01/contents
```

This command will print the path to the folder.

Using the provider name:

```
moth path acme::cafe01
```

Using the alias:

```
moth path quark
```

You can use this from a shell prompt:

```
cat "$(moth path quark)/hello.txt"
```

You can also run commands:

```
moth exec quark hello
```

There are low-level ("plumbing") commands as well:

```
moth get --out-file /tmp/hello.txt facade01:cafe01 --repo-base base
```

Also for uploading:

```
moth put --in-file /tmp/hello.txt facade0 --repo-base base
```
