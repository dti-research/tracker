Tracker Requirements
====================

This document contains the list of requirements for Tracker to fulfill along 
with definitions of key concepts and payoffs.

This project is heavily inspired by Guild AI.

## Concepts

We acknowledge that using Tracker can seem a bit overwhelming to begin with, 
so here are a few definitions that will help you get started:

- **Projects:** At the highest level of abstraction lies the *project* which 
  is created by invoking the command: `tracker create CONF_FILE.yaml`. The 
  project will contain all *experiments* and *trials* (definitions below).
- **Experiments:** At the next level we have *experiments* which denotes 
  specific parameter configurations (or ranges for the automatic hyper-parameter
  optimisation). An experiment physically consists of a configuration file
  similar to the one we use to create the project, but instead of containing
  template URLs, etc. the experiment configuration file contains the specific
  parameter configuration for the algorithm(s), environment(s), and so on.
  Experiments are created by invoking `tracker experiments create NAME`.
- **Trials:** At the lowest level we have *trials* which denotes a single run
  of a specific experiment. When we're evaluating probabilistic models we need
  the ability to conduct multiple repetitions (trials) of the same experiment
  in order to account for the stochasticity of the methods deployed.

## Requirements

Here follows the list of requirements that we set out for Tracker in the order
of workflow.

Tracker can:

1. **Create a project (structure)** from a project template based on the
   [Cookiecutter project](https://github.com/cookiecutter/cookiecutter).
   Any project template based on cookiecutter templating can be used.
   *Why?* To allow for the use of a (more or less) standardised project
   organisation within the company or institution. This allows for easier
   collaboration and sharing amongst coworkers.
1. **Create configuration files** for your experiments.
   *Why?* So you seperate the configuration of your models, algorithms and
   environments from the definitions of those. This can help you remember all
   (hyper-)parameters when you're reporting your results.
1. **Seperate training from validation** (reinforcement learning (RL) specific)
   as we know it from supervised deep learning (DL) where you have a training,
   potentially a validation, and test set. *Why?* To do more correct analysis
   of performance and give the developer an idea of overfitting or
   overspecialisation.
1. **Track all trials** and link them to Git hashes so you always are able to
   go back in time, if your optimisation suddenly starts to regress.
   *Why?* Because real men does backups!
1. **Remotely train and optimise** your model (currently only through SSH)
   without all the hassle. Simply define the remote location with a name and
   an IP adress and Tracker will take care of copying needed files and setting
   up the environment on the remote machine.
1. **Automatically captures** (hyper-)parameters and logs them.
1. **Automatically optimise** your model's parameters. You can choose between
   several different algorithms including: grid search, random search,
   Bayesian, hyperband and Bayesian hyperband (BOHP).
1. **Compare different trials and experiments** to allow you to do what you do
   best *analyse* differences and better understand results.
1. **Ensure the reproducibility** of your work and research. For instance, if
   you do not provide Tracker with a random seed, Tracker will generate a list
   of preset seeds which will be used for the trial(s) selected to be
   conducted.
1. **Back up trained models** to cloud storage (SSH, S3 buckets, MS Azure,
   Google Cloud, B2 (Black Blaze), ...?)

## What's the Payoff?

- You **know** when you're improving and when you're regressing
- You can **go back in time** with git hashes linked to each experiment
  and even trial.
- You can **analyse** differences across runs to better understand results
- You can **collaborate** with colleagues as they know the folder structure
- You can **share** your results with colleagues
- You can **save** and **backup** trained models
- You can **automatically optimise** your model 
- You can make **guarantees** about model performances
- You ensure the **reproducibility** of your work

