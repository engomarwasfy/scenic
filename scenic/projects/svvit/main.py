"""Main file for FastViT."""

from typing import Any

from absl import flags
from clu import metric_writers
import jax
import jax.numpy as jnp
import ml_collections
from scenic import app
from scenic.projects.svvit import classification_trainer
from scenic.projects.svvit import inference
from scenic.projects.svvit import transfer_trainer
from scenic.projects.svvit import vit
from scenic.projects.svvit import xvit
# pylint: disable=unused-import
from scenic.projects.svvit.datasets import pileup_coverage_dataset
from scenic.projects.svvit.datasets import pileup_window_dataset
# pylint: enable=unused-import
from scenic.train_lib_deprecated import train_utils
from scenic.train_lib_deprecated import trainers

FLAGS = flags.FLAGS


def get_model_cls(model_name: str) -> Any:
  """Returns model class given its name."""
  if model_name == 'xvit_classification':
    return xvit.XViTClassificationModel
  elif model_name == 'vit_classification':
    return vit.ViTClassificationModel
  elif model_name == 'topological_vit_classification':
    return vit.TopologicalViTClassificationModel
  else:
    raise ValueError(f'Unrecognized model: {model_name}.')


def get_trainer(trainer_name: str) -> Any:
  """Gets the trainer matching the given name."""
  if trainer_name == 'classification_trainer':
    return classification_trainer.train
  elif trainer_name == 'transfer_trainer':
    return transfer_trainer.train
  else:
    return trainers.get_trainer(trainer_name)


def main(rng: jnp.ndarray, config: ml_collections.ConfigDict, workdir: str,
         writer: metric_writers.MetricWriter):
  """Main function for SVViT."""
  model_cls = get_model_cls(config.model_name)
  data_rng, rng = jax.random.split(rng)

  if config.trainer_name == 'inference':
    inference.evaluate(
        rng=rng,
        eval_config=config,
        model_cls=model_cls,
        workdir=workdir,
        writer=writer)
  else:
    dataset = train_utils.get_dataset(
        config, data_rng, dataset_service_address=FLAGS.dataset_service_address)

    get_trainer(config.trainer_name)(
        rng=rng,
        config=config,
        model_cls=model_cls,
        dataset=dataset,
        workdir=workdir,
        writer=writer)


if __name__ == '__main__':
  app.run(main)
