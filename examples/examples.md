# [Examples](../notebooks/examples.ipynb) #

This notebook demonstrates usage of IBM qiskit, how to deal in this repository with circuits to be executed on the simulator, and those to be properly run on the backend ('queue').

## Demonstration ##

See [examples/examples.md](../examples/examples.md).


```python
'''IMPORTS'''
...
```


```python
'''Example circuit'''
...
```

    Example quantum circuit




![png](examples_files/examples_2_1.png)




```python
'''Example usage of simulator'''
...
```

    Example quantum circuit with simulator




![png](examples_files/examples_3_1.png)



    NOTE:
    - backend: aer_simulator
    - job id: *****




![png](examples_files/examples_3_3.png)





![png](examples_files/examples_3_4.png)





![png](examples_files/examples_3_5.png)




```python
'''Display list of IBM backend options'''
...
```

    AVAILABLE BACKENDS (SIMULATOR):
    - ibmq_qasm_simulator
    - simulator_statevector
    - simulator_mps
    - simulator_extended_stabilizer
    - simulator_stabilizer
    ----
    AVAILABLE BACKENDS (QUEUE):
    - ibmq_lima
    - ibmq_belem
    - ibmq_quito
    - ibmq_manila
    - ibm_nairobi
    - ibm_oslo



```python
'''Example usage of IBM cloud backend (queue)'''
...
```


```python
'''Statistics for backend job - NOTE: job may be pending'''
...
```



![png](examples_files/examples_6_0.png)





![png](examples_files/examples_6_1.png)





![png](examples_files/examples_6_2.png)
