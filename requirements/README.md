## Initial Questions :question: :question: :question:

This is a draft to determine what are the main problems for this project.

### As a DevOp i want to...

1. What is the neighbourhood of one service? 
    1. Incoming requests (What service).
    2. Outgoing requests (What service).
2. Is there any problem (Wich are the associated heuristics)?
    1. Response time (Delta).
    2. Morphology/Topology (Delta).
    3. Ocupation/Load (Delta) (Queue length).
    4. Number/Profile(Same/different IP's) of the client (Delta).
3. Is there any faults related to the system design/architecture?
    1. Is there cyclical dependencies?
        1. Error rate correlation.
    2. Multiple calls in the same request.
4. What is the root problem?
    1. A, B, C services are slow, so what is the root problem?
        1. Load variation.
        2. Change(Add/Remove) in the dependencies.
5. How are the requests coming from the client?
    1. Quantity.
    2. Profile.
6. How endpoints orders distributions are done?
    1. Use of a specific endpoint.
    2. Which endpoints are the most popular?
        1. Endpoint requests.
7. What is the behaviour of the instances?
    1. How do we know if a certain instance is in a "normal state"?
        1. Relatively to other instances.
        2. Relatively to the instance "normal state".
    2. Number of instances
        1. Relatively to the load.
        2. Relatively to the occupation.

### Notes: 

2.1.1.4. and 5.1. are related.

6.2. The popularity of a service defines it's importance.

### Vizualization:
1. How will we do the data aggregation?
