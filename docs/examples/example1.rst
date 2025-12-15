.. _example1:

Reproduce the results of the paper.
===================================

NEMAT allows you to create a starting directory with the precomputed input files used in the paper (`preprint <https://www.biorxiv.org/content/10.64898/2025.12.09.692605v1>`_). Follow these steps:

1. Create a new directory (for example, *nemat_test*).
2. ``cd nemat_test``
3. ``nemat example``
4. You can now follow the steps from :ref:`here <run_nemat>`.

In case you want to reproduce the 6a analogues (Tab. 2), you must change the edges in ``input.yaml`` with:

.. code-block:: yaml

    edges:                                 # List of lists containing the edges.  
        - ['6a', '6i']
        - ['6a', '6f']
        - ['6a', '6h']
        - ['6a', '6m']
        - ['6a', '6g']
        - ['6a', '6l']
        - ['6a', '6j']
        - ['6a', '6n']  
