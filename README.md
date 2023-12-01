# What are benefits of using solara and why choose solara for next app?

- Define your UI based on the state/data (declarative, like ReactJS)Auto re-executes what is needed (reactive, like Excel)
- Reusability / encapsulation (components)
- you can write new ones using the underlying library (ipyvuetify)
- you can use html/css/js/vue/react to write your own widgets if needed
- Together they make it possible to take on larger projects and don't get stuck.
- it's nice to be able to just call the python functions you want to use instead of going through REST api's etc.

# Install locally

```
pip install -e .
```

# Run locally

```
$ solara run solarathon.pages
# add --no-open if you don't like opening the browser window automatically
```

# Deploy via Github Actions

[Get your Ploomber API key](https://docs.cloud.ploomber.io/en/latest/quickstart/apikey.html) and set it as `PLOOMBER_CLOUD_KEY` in GitHub (under Settings->Secrets and Variables->Actions, and click "New repository secret")

## Do only once

- [Sign up for Ploomber](https://www.platform.ploomber.io/register/)
- [Get the API key](https://docs.cloud.ploomber.io/en/latest/quickstart/apikey.html) from [The Ploomber dashboard](https://platform.ploomber.io/)

```
$ ploomber-cloud key YOURKEY
$ (cd ploomber && rm ploomber-cloud.json && ploomber-cloud init)
(add to git and commit)
$ git add ploomber/ploomber-cloud.json
$ git commit -m "ci: set ploomber id"
$ git push origin master:ploomber
```

## Run to deploy a new version

```
$ git push origin master:ploomber
# add --force if needed
```

# Other resources

- [Wanderlust app](https://github.com/widgetti/wanderlust)
- [Solara website](https://github.com/widgetti/solara/tree/master/solara/website)
- [Solara examples](https://solara.dev/examples)

# Deploy manually

(Not recommended)
See https://docs.cloud.ploomber.io/en/latest/user-guide/cli.html for more details

```
$ pip install ploomber-cloud
$ mkdir -p ploomber/wheels
$ ploomber-cloud key YOURKEY
$ (cd ploomber && ploomber-cloud init)
(type y)
# build the wheel
$ (hatch build && cp dist/*.whl ploomber/wheels)
$ (cd ploomber && ploomber-cloud deploy)
```
