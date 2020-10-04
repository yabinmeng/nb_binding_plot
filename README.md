# Overview

[NoSQLBench (NB)](https://github.com/nosqlbench/nosqlbench) is a very powerful performance testing and workload generation tool for a NoSQL ecosystem like Cassandra, Kafak, and etc. Overall it is simple to use. It defines testing scenarios in a YAML that is quite straightforward and self-explanatory for the most part. 

Within NB, the core component for workload generation is binding function (flow). NB documentation web site has a dedicated [section](http://docs.nosqlbench.io/#/docs/bindings) that briefly explains the binding concept and describes all available binding functions in NB.

For many new NB users, NB binding function is probably the most challenging part of creating a proper scenario definition file. In many cases, the challenge really comes from the fact as as user, it is hard to see what a particular binding function is going to produce. 

## Using NB's "stdout" Driver 

One way to quickly check binding function outputs is to define a scenario definition file that only contains binding definitions and then execute it using NB's "**stdout**" driver. The procedure is as below:

* Create a scenario definition file (e.g. MyBinding.yaml)
```
bindings:
  foo: SaveLong('cycle'); CoinFunc(0.5, FixedValue(-10), FixedValue(10))
  bar: T(2); Add(10)
```

* Execute using **stdout** driver
```
$ ./nb run driver=stdout workload=MyBinding.yaml cycles=10
Logging to logs/scenario_20201004_150742_288.log
t=9.451913992436708 savelong=-10
t=10.553459342042853 savelong=10
t=11.775443926493887 savelong=10
t=11.580608821696428 savelong=10
t=8.930814293546522 savelong=-10
t=9.954798431622152 savelong=-10
t=10.544348872282352 savelong=10
t=10.13139344448723 savelong=10
t=9.807465364476807 savelong=-10
t=9.330448775944763 savelong=-10
```

In the above example, there are 2 binding function flows (named as "foo" and "bar" respectively). Using NB's **stdout** driver, we can see how the binding function output looks like for each iteration of the execution cycle. This will help better understand each binding function.

# Plot Binding Function Results

Based on the above discussion of using NB's **stdout** driver to view binding function outputs, the python program in this repository makes it further to plot the binding function output using a graph. 

For example, for the previous 2 binding function flows, their plotted graphs look like below:

<img src="https://github.com/yabinmeng/nb_binding_plot/blob/master/screenshots/bindingplot1.png" width=500> 

## Pre-requisites and Limitations

## Execute the Script
