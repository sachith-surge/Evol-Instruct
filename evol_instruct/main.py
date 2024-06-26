import configparser

import modal
from modal import Image
from pyprojroot import here

# Initialize modal app
app = modal.App()

# Setup volume for storing model weights
volume = modal.Volume.from_name("evol-instruct", create_if_missing=True)
MODEL_DIR = "/vol"

# Setup GPU
config = configparser.ConfigParser()
config.optionxform = str
config.read(here('evol_instruct/config/config.ini'))

GPU = config['modal']['GPU']

image = (
    Image.from_registry("thr3a/cuda12.1-torch")
    .poetry_install_from_file(poetry_pyproject_toml="pyproject.toml")
)


@app.function(
    gpu=GPU,
    timeout=86400, # Allow one day timout period
    image=image,
    mounts=[
        modal.Mount.from_local_file('setup.py', '/root/setup.py'),
        modal.Mount.from_local_python_packages('evol_instruct'),
    ],
    volumes={
        MODEL_DIR: volume
    },
    _allow_background_volume_commits=True
)
def run_on_modal(
    run_on_remote: bool = True
):
    from pyprojroot import here
    import subprocess
    import os
    import configparser

    from evol_instruct.init.logger import logger

    config = configparser.ConfigParser()
    config.read(here('evol_instruct/config/config.ini'))
    
    if run_on_remote:
        logger.info('Running on Modal. Setting HF_HUB_CACHE to /vol/.cache. This will download the models to the Modal Volume, allowing subsequent runs to load models from the cache.')
        os.environ['HF_HUB_CACHE'] = '/vol/.cache'

        # Need to update the config file if this script is run on remote
        config['modal']['RunOnModal'] = "True"
        with open(here('evol_instruct/config/config.ini'), 'w') as configfile:
            config.write(configfile)

    from evol_instruct.data.prepare_seed import prepare_seed_datasets
    from evol_instruct.init.model import generator_model_path, evaluator_model_ggml_path, evaluator_model_gguf_path
    from evol_instruct.helpers.bash import run_bash_script_in_background
    from evol_instruct.helpers.evolver import evolve_dataset

    # Load the dataset config file
    dataset_config = configparser.ConfigParser()
    dataset_config.read(here(config['data']['ConfigurationFile']))

    # Prepare the generator model
    logger.info('Dispatching prepare_generator_model.sh to run in the background')

    prepare_generator_model_script = here('evol_instruct/scripts/prepare_generator_model.sh')
    subprocess.run(['chmod', '+x', prepare_generator_model_script], check=True)
    pgm_process = run_bash_script_in_background(prepare_generator_model_script, args=['-O', os.path.dirname(generator_model_path)], cwd=here('evol_instruct/workers'))

    # Prepare the evaluator model
    logger.info('Dispatching prepare_evaluator_model.sh to run in the background')

    prepare_evaluator_model_script = here('evol_instruct/scripts/prepare_evaluator_model.sh')
    subprocess.run(['chmod', '+x', prepare_evaluator_model_script], check=True)
    pem_process = run_bash_script_in_background(prepare_evaluator_model_script, args=['-i', evaluator_model_ggml_path, '-o', evaluator_model_gguf_path], cwd=here('evol_instruct/workers'))


    data = prepare_seed_datasets()

    logger.info('Waiting for dispatched scripts to finish compiling')
    pgm_process.communicate()
    logger.info('Generator model script finished compiling')
    pem_process.communicate()
    logger.info('Evaluator model script finished compiling')
    pgm_process.kill()
    pem_process.kill()

    logger.info('Starting evolution process')

    evolve_dataset(dataset_config, data)
    

@app.local_entrypoint()
def main(
    run_on_remote: bool = True
):
    if run_on_remote:
        run_on_modal.remote(run_on_remote)
    else:
        config['modal']['RunOnModal'] = "False"
        with open(here('evol_instruct/config/config.ini'), 'w') as configfile:
            config.write(configfile)

        run_on_modal.local(run_on_remote)