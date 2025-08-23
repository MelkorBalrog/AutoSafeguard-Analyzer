from analysis.causal_bayesian_network import CausalBayesianNetwork, CausalBayesianNetworkDoc
from analysis.scenario_bn import build_bn_from_scenario


def _is_chain(doc, root, elements):
    parents = doc.network.parents
    prev = root
    for elem in elements:
        if parents.get(elem) != [prev]:
            return False
        prev = elem
    return parents.get(root) == []


def test_select_best_bn_version():
    scenario = {"name": "Scenario", "description": "[[A]] then [[B]]"}
    elements = ["A", "B"]

    def v1(scen):
        net = CausalBayesianNetwork()
        prev = None
        for name in elements:
            if prev:
                net.add_node(name, parents=[prev], cpd={(True,): 0.5, (False,): 0.5})
            else:
                net.add_node(name, cpd=0.5)
            prev = name
        return CausalBayesianNetworkDoc("v1", network=net)

    def v2(scen):
        net = CausalBayesianNetwork()
        root = scen["name"]
        net.add_node(root, cpd=0.5)
        for name in elements:
            net.add_node(name, parents=[root], cpd={(True,): 0.5, (False,): 0.5})
        return CausalBayesianNetworkDoc("v2", network=net)

    def v3(scen):
        net = CausalBayesianNetwork()
        root = scen["name"]
        net.add_node(root, cpd=0.5)
        prev = root
        for name in elements:
            net.add_node(name, parents=[prev], cpd={(True,): 0.5, (False,): 0.5})
            prev = name
        return CausalBayesianNetworkDoc("v3", network=net)

    def v4(scen):
        net = CausalBayesianNetwork()
        root = scen["name"]
        net.add_node(root, cpd=0.5)
        net.add_node(elements[0], parents=[root], cpd={(True,): 0.5, (False,): 0.5})
        net.add_node(
            elements[1], parents=[root, elements[0]], cpd={(True, True): 0.5, (False, False): 0.5}
        )
        return CausalBayesianNetworkDoc("v4", network=net)

    docs = [v1(scenario), v2(scenario), v3(scenario), v4(scenario)]
    chain_results = [_is_chain(doc, scenario["name"], elements) for doc in docs]
    assert chain_results == [False, False, True, False]

    final_doc = build_bn_from_scenario(scenario)
    assert _is_chain(final_doc, scenario["name"], elements)
