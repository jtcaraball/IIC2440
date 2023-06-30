# IIC2440 - Tarea 2

## Dependencies

- `pyspark`

## How to run

To run the any of the two notebooks in Google Colab first run the graph
generation script locally with one of the commands bellow to create a random
graph of given dimensions:

Page Rank:
```
$ python3 graph_util.py simple {n_nodes} {n_edges}
```

SSSP:
```
$ python3 graph_util.py costs {n_nodes} {n_edges}
```

Then upload the resulting file (`graph.json` for Page Rank or
`graph_costs.json` for SSSP) to your Colab environment and run the
corresponding notebook.

**Note 1**: For larger graphs the variable `MAX_PARTITIONS` should be set to a
higher number. The reason why we set is to prevent Spark from duplicating the
number of partitions exponentially (which leads to exponential execute times)
on iteration that use the `join` and `reduceByKey` primitives.

**Note 2**: The notebooks are generally 10x slower running on Colab over
running them localy on a i7-8700k cpu.

## General strategy

You can see a general strategy to solving distributed graph problems
[here](https://youtu.be/FtOcb2t8S0o).
