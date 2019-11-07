## Droplets
Droplets are ready to use scenarios where infra and provisioning are automatically provided. You can see the available droplets [here](https://github.com/moondly/droplets)

## Usage
### Apply a droplet
1. Make sure you are inside foglab (vagrant ssh)
1. Get the latest droplet libs
    ```
    dropctl init            (only the first time)
    dropctl init --update   (to get updates)
    ```
1. Create a lab folder and change to it
    ```
    mkdir mylab
    cd mylab
    ```
1. Apply the droplet to your lab
    ```
    dropctl apply swarmGluster
    ```

This will create a folder in your lab with the droplet config

### Destroy a droplet
```
cd mylab
dropctl destroy swarmGluster
```

### Adapt the droplet infra
You can edit at any time the `infra.tf` file under the droplet folder and call:
```
droplet apply swarmGluster --phases infra
``` 
to apply the changes.
