# api.harold.kim

It's just the backend API server for harold.kim and its subdomains

Gameboy endpoint is not included in this repository.

Sourcecode that interacts with private API services / servers are not included within this code.

```
class Proseka(Resource):
    """ /api/v1/proseka: Proseka Information """
    def get(self):
        """ grabs the output from the scheduled task. """
        return json.loads(open(os.path.join("data", "proseka.json"), "rb").read())
```

It's intentionally left to load data everytime as to ensure that it gets refreshed as soon as possible.

There are cache problems so I'm skipping other sorts of methods that minimizes the load of this process..
