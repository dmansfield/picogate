# picogate

*IMPORTANT* the Pico micropython script requires some secrets to be configured
in it. In order to prevent this from being pushed to the repository, a git
filter is used.

You'll need to configure your repository before using it by importing the
configuration file provided, .gitsharedconfig.

```
git config --local include.path ../.gitsharedconfig
```
