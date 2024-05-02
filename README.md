
# AutoML in Heavily Constrained Applications

This is the code to the paper 
[**"AutoML in Heavily Constrained Applications"**](https://arxiv.org/pdf/2306.16913.pdf) 
by Felix Neutatz, Marius Lindauer, and Ziawasch Abedjan
which was published in the International Journal on Very Large Data Bases.

If you have questions or want to contribute, please refer to the official repository.

---


 Abstract:
>Optimizing a machine learning pipeline for a task at hand requires careful configuration of various hyperparameters, typically supported by an AutoML system that optimizes the hyperparameters for the given training dataset. Yet, depending on the AutoML system’s own second-order meta-configuration, the performance of the AutoML process can vary significantly. Current AutoML systems cannot automatically adapt their own configuration to a specific use case. Further, they cannot compile user-defined application constraints on the effectiveness and efficiency of the pipeline and its generation. In this paper, we propose Caml, which uses meta-learning to automatically adapt its own AutoML parameters, such as the search strategy, the validation strategy, and the search space, for a task at hand. The dynamic AutoML strategy of Caml takes user-defined constraints into account and obtains constraint-satisfying pipelines with high predictive performance.

We invite the reader to have a look at our paper and the code to reproduce our
results. All details necessary to understand the code and hyperparameter are 
given in the paper.

![image](https://user-images.githubusercontent.com/5217389/216223724-05dd746d-4cce-4e64-869e-b791cfe7cee2.png)

Credit Stable Diffusion

---
## Install

Checkout the repository:

```bash
git clone https://github.com/GreenAutoML4FAS/AutoMLInHeavilyConstrainedApplications
cd AutoMLInHeavilyConstrainedApplications
```

Create a new invironment and set it up:

```bash
conda create -n AutoMLD python=3.7
conda activate AutoMLD
cd Software/DeclarativeAutoML/
git pull origin main
sh setup.sh
```

## Run CAML in four lines of code

```python
from fastsklearnfeature.declarative_automl.caml.CAML import CAML

caml = CAML(time_search_budget=60, inference_time_limit=0.001)
caml.fit(X_train, y_train, categorical_indicator)
y_pred = caml.predict(X_test)
```

## Example
Check out the [example notebook](https://colab.research.google.com/drive/1z8EnNQnik5gNKSTf38YIDGk4ivJlRVpi?usp=sharing) of CAML!


## Citation

If you find this work useful, please include the following citation:

```latex
@inproceedings{caml,
    title     = {AutoML in Heavily Constrained Applications},
    author    = {Felix Neutatz and
                  Marius Lindauer and
                  Ziawasch Abedjan},
    booktitle = {VLDB Journal},
    year      = {2023}
}
```

---

## License Notice

The **content of this repository** is licensed under the BSD-3-Clause license.

## Acknowledgement
This work was partially supported by the Federal Ministry of the Environment, 
Nature 
Conservation, Nuclear Safety and Consumer Protection, Germany under the project 
**GreenAutoML4FAS** (grant no. 67KI32007A). 

The work was done at the Leibniz University Hannover and published in the *International Journal on Very Large Data Bases* 2023.

<p align="center">
    <img width="100" height="100" src="fig/AutoML4FAS_Logo.jpeg"> 
    <img width="300" height="100" src="fig/Bund.png">
    <img width="300" height="100" src="fig/LUH.png"> 
</p>
