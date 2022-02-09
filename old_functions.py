import cProfile
import copy
import pickle
import pstats
import time

import matplotlib
import networkx as nx
import numpy as np
from matplotlib import pyplot as plt

import example_graphs
import non_reversible_graphs
import square_graph
import signal_processing


def triangletester():
    # g.show('tri.html',color_roots=True)
    # g.show('tri2.html',color_roots=False)
    counter = 0
    N = 7000
    for a in [.2]:
        debugger = []
        g = non_reversible_graphs.Triangle(a)
        qlist = [.7 * a, .8 * a, .85 * a, .9 * a, .93 * a, .95 * a, .97 * a, .98 * a, .99 * a, .995 * a, a, 1.02 * a,
                 1.3 * a]
        for q in qlist:
            hist = np.zeros(7)
            for _ in range(N):
                g.wilson(q)
                for i in range(1, 4):
                    if g.roots == {i}:
                        hist[i - 1] += 1
                    if g.roots == {1, 2, 3} - {i}:
                        hist[i + 2] += 1
                if g.roots == {1, 2, 3}:
                    hist[6] += 1
            plt.plot(["{1}", "{2}", "{3}", "{2,3}", "{1,3}", "{1,2}", "{1,2,3}"], hist / N, label=q)
            debugger.append(hist[0] / N)
        print(hist, sum(hist))
        plt.plot(np.array(qlist) / a, debugger)
        plt.legend()
        plt.show()


def triangleoptimizer():
    samplesize = 40000
    for a in [0, .001, .01, .05, .1, .4, .9]:
        g = non_reversible_graphs.Triangle(a)
        qlist = []
        plist = []
        for q in [i / 5 + .1 for i in range(15)]:
            qlist.append(q)
            plist.append(0)
            for _ in range(samplesize):
                g.wilson(q)
                if g.roots == {2, 3}:
                    plist[-1] += 1 / samplesize
        plt.plot(qlist, plist, label='a=' + str(a))
    plt.legend()
    plt.show()


def showhalfer_singletons():
    N = 100
    samplesize = 5000
    g = non_reversible_graphs.Halfer(N)
    zero_counter = 0
    singelton = 0
    hist = np.zeros(N + 1)
    for _ in range(samplesize):
        g.wilson(.0031)
        for j in range(N + 1):
            if g.roots == {j}:
                hist[j] += 1
        if g.roots == {0}:
            zero_counter += 1
        if len(g.roots) == 1:
            singelton += 1
    print(zero_counter / samplesize)
    print(singelton / samplesize)
    print(zero_counter / singelton)
    hist = np.array(hist)
    plt.plot(range(7), hist[:7] / singelton)
    plt.plot(range(7), np.array([1, 1, .5, .25, .125, 1 / 16, 1 / 32]) / 3)
    plt.show()
    g.show('gegenbeispiel.html')


def showhalfer_q():
    N = 100
    samplesize = 100
    g = non_reversible_graphs.Halfer(N)
    qlist = [.001, .002, .004, .007, .01, .02, .03, .05, .07, .1]
    K = len(qlist)
    hist1 = np.zeros(K)
    hist2 = np.zeros(K)
    hist3 = np.zeros(K)
    hist4 = np.zeros(K)
    for _ in range(samplesize):
        for j in range(K):
            g.wilson(qlist[j])
            if len(g.roots) == 1:
                hist1[j] += 1
            if len(g.roots) == 2:
                hist2[j] += 1
            if len(g.roots) == 3:
                hist3[j] += 1
            if len(g.roots) == 4:
                hist4[j] += 1
    plt.plot(qlist, hist1 / samplesize, label='one root')
    plt.plot(qlist, hist2 / samplesize, label='two roots')
    plt.plot(qlist, hist3 / samplesize, label='three roots')
    plt.plot(qlist, hist4 / samplesize, label='four roots')
    plt.legend()
    plt.show()


def laufzeitentest_ana_recr():
    nlist = []
    alist = []
    rlist = []
    slist = []
    for i in range(14):
        n = 7 * i + 10
        g = square_graph.SquareSignalProcessingGraph(n)
        g.wilson(.6)
        g.number_the_nodes()
        temp = time.time()
        g.analysis_operator(.3)
        alist.append(time.time() - temp)
        temp = time.time()
        L_Schur = g.compute_Schur_complement()
        slist.append(time.time() - temp)
        temp = time.time()
        g.reconstruction_operator(.3, L_Schur=L_Schur)
        rlist.append(time.time() - temp)
        nlist.append(n)
    alist = np.array(alist)
    alist = alist ** .25
    rlist = np.array(rlist)
    rlist = rlist ** .25
    slist = np.array(slist)
    slist = slist ** .25
    plt.plot(nlist, alist, label='ana')
    plt.plot(nlist, slist, label='nur Schur')
    plt.plot(nlist, rlist, label='reconstr')
    plt.legend()
    plt.show()


def recruntersuchung():
    a = .3
    g = non_reversible_graphs.Triangle(a)
    g.wilson(.01)
    while g.roots != {2, 3}:
        g.wilson(.01)
    print(g.roots)
    L_Schur = g.compute_Schur_complement()
    g.reconstruction_operator(.2, L_Schur=L_Schur)
    g.show('recr_tri.html', color_roots=False)


def halfer_tester_multiresolution():
    g = non_reversible_graphs.Halfer(N=100)
    g.wilson(1.23456789)
    g.set_weights()
    g.show('original.html', color_roots=False)
    time.sleep(1)
    print(f"{g.graph['alpha']=}")
    with cProfile.Profile() as pr:
        g2 = g.one_step_in_multiresolution_scheme()
        print('///////////////////////////')
        for n in g2.nodes:
            print(n, g2.nodes[n]['value'])
        time.sleep(1)
        g3 = g2.one_step_in_multiresolution_scheme()
        time.sleep(1)
        g4 = g3.one_step_in_multiresolution_scheme()
        time.sleep(1)
        g5 = g4.one_step_in_multiresolution_scheme()
        time.sleep(1)
        g6 = g5.one_step_in_multiresolution_scheme()
    stats = pstats.Stats(pr)
    stats.sort_stats(pstats.SortKey.TIME)
    stats.print_stats()


def funktionstest():
    g1 = square_graph.SquareSignalProcessingGraph(30, standardweights=False)
    g1.wilson(1.23456789)
    g1.show('g.html', color_roots=False)
    g2, q1, qp1 = g1.one_step_in_multiresolution_scheme()
    g3, q2, qp2 = g2.one_step_in_multiresolution_scheme()
    g2.copy_values_from_other_graph_wherever_they_exist(g3)
    g2.set_non_root_values_to_zero()
    g2.reconstruction_operator(qp2)
    g2.show('g2.html', color_roots=False)
    g1.copy_values_from_other_graph_wherever_they_exist(g2)
    g1.set_non_root_values_to_zero()
    g1.reconstruction_operator(qp1)
    g1.show('g1.html', color_roots=False)


def save_multistep_to_file(steps=5, g=None, name_of_graph='graph'):
    if g is None:
        g = example_graphs.WattsStrogatzGraph(100, 5, .3)

    # g = square_graph.SquareSignalProcessingGraph(60, standardweights=False)
    # g.wilson(1.23456789)
    # q_list, q_prime_list, graph_list=wilson.multi_resolution_and_reconstr(g,3)
    # g.draw_optimizer_path(.01,1000)
    # g.coupled_cont(3,2.7)
    # g.show('g.html',)
    q_list, q_prime_list, graph_list = signal_processing.multiresolution(g, steps=steps)
    print('q_list')
    print(q_list)
    print('q_prime_list')
    print(q_prime_list)
    print('graph_list')
    print(graph_list)
    result = [q_list, q_prime_list, graph_list]
    with open(f'multi_res_{name_of_graph}_{steps}_steps.pkl', 'wb') as file:
        pickle.dump(result, file)
    return result


def read_multi_and_do_stuff(steps=5, g=None, name_of_graph='graph'):
    with open(f'multi_res_{name_of_graph}_{steps}_steps.pkl', 'rb') as file:
        if g is None:
            g = example_graphs.WattsStrogatzGraph(100, 5, .3)

        q_list, q_prime_list, graph_list = pickle.load(file)
        print(q_list, q_prime_list, graph_list)
        signal_processing.multi_reconstr(graph_list[:], q_prime_list[:], )


def test_R():
    g = square_graph.SquareSignalProcessingGraph(60, standardweights=False)
    g.wilson(1.23456789)
    g2, q, q_prime = g.one_step_in_multiresolution_scheme(name_of_graph=f'downsampling_step')
    g2.show("g2.html", color_roots=False)
    print(g2 is g)
    g.show("g.html", color_roots=False)
    g.set_all_values_to_zero()
    g.copy_values_from_other_graph_wherever_they_exist(g2)
    g.show('g.html', color_roots=False)
    print(f'{len(g.roots)=}')
    for i in range(2):
        g.show('g_old.html', color_roots=False)
        _g = copy.deepcopy(g)
        print(g is _g)
        _g.reconstruction_operator(q_prime * (.4 + .1 * i))
        g.show('g_new.html', color_roots=False)
        _g.show('_g.html', color_roots=False)
    g.show('end.html', color_roots=False)


def compare_the_two_creation_methods_of_the_Laplacian():
    size = []
    time_list = []
    time2_list = []
    for i in range(10):
        s = 30 + 10 * i
        size.append(s)
        g = square_graph.SquareSignalProcessingGraph(s, standardweights=False)
        g.wilson(1.23456789)
        t = time.perf_counter()
        L = g.create_Laplacian()
        time_list.append(time.perf_counter() - t)
        t = time.perf_counter()
        L = g.create_Laplacian2()
        time2_list.append(time.perf_counter() - t)

    plt.plot(size, np.array(time_list) ** .5, label='square root of time')
    plt.plot(size, np.array(time2_list) ** .5, label='square root of time2')
    plt.legend()
    plt.show()
    print(time_list)
    print(time2_list)
    # save_multistep_to_file(3)
    # read_multi_and_do_stuff(3)


def test_coupling_distribution(N: int):
    g = non_reversible_graphs.Halfer(N)
    q_final = g.coupled_cont(10, .004)
    print(f'(We are in testing function... {q_final=}')
    res = np.zeros(N + 1)
    # g.show('Halfer.html')
    for i in range(N + 1):
        if i in g.roots:
            res[i] = 1
    print('%%%%%%%%%%%%%%%%%%%', g.nodes[0], g.nodes[1])
    return res, q_final


def test_wilson_distribution(N: int, q):
    g = non_reversible_graphs.Halfer(N)
    g.wilson(q)

    res = np.zeros(N + 1)
    # g.show('Halfer.html')
    for i in range(N + 1):
        if i in g.roots:
            res[i] = 1
    return res


def debug_coupled(number_of_tries=100):
    N = 10
    fr = np.zeros(N + 1)
    q_list = []
    for _ in range(number_of_tries):
        res, q_final = test_coupling_distribution(N)
        print(res)
        print(q_final)
        print('----------------')
        fr += res
        q_list.append(q_final)
    print(fr.sum())
    print(fr)
    plt.plot(range(N + 1), fr)
    plt.show()
    fr = np.zeros(N + 1)
    for q in q_list:
        fr += test_wilson_distribution(N, q)
    print(fr.sum())
    print(fr)
    plt.plot(range(N + 1), fr)
    plt.show()


def make_one_complete_multi(steps, graph, name_of_graph):
    g = copy.deepcopy(graph)
    save_multistep_to_file(steps, g, name_of_graph)
    g = copy.deepcopy(graph)
    read_multi_and_do_stuff(steps, g, name_of_graph)


def test_io_for_networkx_and_pdf_creating():
    print('Guten Morgen!')
    g = example_graphs.WattsStrogatzGraph(100, 20, .2)
    g = square_graph.SquareSignalProcessingGraph(90, standardweights=False)
    g.wilson(12.3456)
    # g.show('nodes.html')
    temp = time.perf_counter()
    print([g.nodes[n]['value'] for n in g.nodes])
    g.create_picture('roots.pdf')
    g.create_picture('values.pdf', color_using_roots=False)
    print(time.perf_counter() - temp)

    temp = time.perf_counter()
    nx.write_gexf(g, "test.gexf")
    # g.show('expampleSquare.html', color_roots=False)
    print('gexfdump:', time.perf_counter() - temp)
    temp = time.perf_counter()
    h = nx.read_gexf("test.gexf")
    print('gexfload:', time.perf_counter() - temp)
    temp = time.perf_counter()
    with open('test.pickle', 'wb') as file:
        pickle.dump(g, file)
    print('pickledump:', time.perf_counter() - temp)
    temp = time.perf_counter()
    with open('test.pickle', 'rb') as file:
        h = pickle.load(file)
    print('pickleload:', time.perf_counter() - temp)
    # h.show('g.html')

    # with open('multi_res_facebook_3_steps.pkl', 'rb') as file:  Reading in takes 70? seconds
    # with open('multi_res_5_steps_on_60_square.pkl', 'rb') as file:  # Reading in takes 128.20001770000002 seconds
    #     q_list, q_prime_list, graph_list = pickle.load(file)
    # print(f'Reading in takes {time.perf_counter() - temp} seconds')
    # print('************************')
    # print(q_list)
    # print(q_prime_list)
    # print(graph_list)
    # for g in graph_list:
    #    print(g.roots)
    #    g.show('g_60_temp.html', color_roots=False)
    # make_one_complete_multi(3, g, 'facebook')  # Takes about 20 min
    # g.wilson(3.45)
    # g.show('facebook.html')
    # g.show('facebook.html',color_roots=False)


def pdf_alternative():
    g = square_graph.SquareSignalProcessingGraph(90, standardweights=False)
    g.stack_version_of_wilson(1.234, start_from_scratch=True, )
    g.create_picture(vmin=-10000, vmax=10000, color_using_roots=False)
    for _ in range(1):
        temp = time.perf_counter()
        g.stack_version_of_wilson(12.3456, start_from_scratch=True)
        print(time.perf_counter() - temp)
        # g.show('gg.html')

    for _ in range(0):
        g.wilson(1.234)
    plt.clf()
    plt.scatter(
        x=[g.nodes[n]['x'] for n in g.nodes],
        y=[g.nodes[n]['y'] for n in g.nodes],
        c=[g.nodes[n]['value'] for n in g.nodes],
        cmap=matplotlib.cm.coolwarm

    )
    x_edges_start = np.array([g.nodes[e[0]]['x'] for e in g.edges if g.edges[e]['hidden'] == False])
    y_edges_start = np.array([g.nodes[e[0]]['y'] for e in g.edges if g.edges[e]['hidden'] == False])
    x_edges_end = np.array([g.nodes[e[1]]['x'] for e in g.edges if g.edges[e]['hidden'] == False])
    y_edges_end = np.array([g.nodes[e[1]]['y'] for e in g.edges if g.edges[e]['hidden'] == False])
    x_edges_diff = x_edges_end - x_edges_start
    y_edges_diff = y_edges_end - y_edges_start
    for i in range(len(x_edges_diff)):
        plt.arrow(x_edges_start[i], y_edges_start[i], x_edges_diff[i], y_edges_diff[i], width=.08)

    plt.show()
    # g.create_picture()


def halfer_root_0_picture():
    g = non_reversible_graphs.Halfer(10)

    g.stack_version_of_wilson(.02, start_from_scratch=True, renumber_roots_after_finishing=True)
    while g.roots != {0}:
        g.stack_version_of_wilson(.02, start_from_scratch=True, renumber_roots_after_finishing=True)
    g.create_picture('halfer_roots.pdf')
    g.create_picture('halfer_color_start.pdf', color_using_roots=False, print_values=True)
    g.analysis_operator(1)
    print([g.nodes[n] for n in g.nodes])
    g.create_picture('halfer_color_ana.pdf', color_using_roots=False, print_values=True)
    g.reconstruction_operator(1)
    g.create_picture('halfer_color_reconstr.pdf', color_using_roots=False, print_values=True)

    print([g.nodes[n] for n in g.nodes])


def save_coupling():
    g = square_graph.SquareSignalProcessingGraph(5)
    i = 0
    q = 3
    g.stack_version_of_wilson(q, renumber_roots_after_finishing=False, start_from_scratch=True)
    m = len(g.roots)
    while q > 1:
        i += 1

        q = g._coupled_q_next(q)
        g.create_picture(f'graph_with_{i=}.pdf', node_size=280, arrowsize=14)

        m = len(g.roots)
        print(i, q)


def print_stored_root_distribution_for_halfer():
    # These are the numbers from a calculation that I did some time ago that took about one hour
    coupled_list = np.array([3310, 3285, 1719, 882, 458, 224, 127, 69, 51, 22, 29.])
    direct_list = np.array([3332, 3457, 1639, 847, 403, 186, 137, 60, 48, 28, 25.])

    samplesize = 10000
    width = .3
    plt.bar(np.arange(11) - width, coupled_list / samplesize, width=width,
            label='Coupling process stopped for q<0.004\nSamplesize:10000')
    plt.bar(np.arange(11), direct_list / samplesize, width=width,
            label="Direct Application of Wilson's algorithm\n for the same q as above\nSamplesize:10000")
    # Now we compute the expected proportions
    exp_list = np.array([1.] + [.5 ** i for i in range(10)])
    exp_list = exp_list / exp_list.sum()
    plt.bar(np.arange(11) + width, exp_list, width=width,
            label="Theoretical probability for q->0")
    plt.xticks(np.arange(11), np.arange(11))
    # plt.title('Probability for a vertex becoming a root: \nNumerical approximations and theoretical results')
    plt.legend()

    plt.show()


def visualize_downsampled_graph_old():
    g = square_graph.SquareSignalProcessingGraph(90)
    g.wilson(9.34)
    L = g.compute_Schur_complement()
    g_downsampled = signal_processing.create_graph_from_matrix(L, g)
    for e in g_downsampled.edges:
        g_downsampled.edges[e]['hidden'] = False
    # g_downsampled.create_picture('downsampled_graph.pdf', color_using_roots=False, colorbar=False, node_color='gray',
    #                         edgelist=g_downsampled.edges,
    #                         colorbar_for_edges=True)
    g_downsampled.set_weights()
    print(g_downsampled.graph['alpha'])
    for n in g_downsampled.nodes:
        print(g_downsampled.nodes[n]['weight'])


def tim_test():
    g = square_graph.SquareSignalProcessingGraph(30, standardweights=False)
    g.wilson(12.345)
    g.analysis_operator(9.876)
    g.show('ana.html', color_roots=False)
    g_copy = copy.deepcopy(g)
    g.reconstruction_operator_without_detail_nodes(9.876)
    g.show('rec_without_det.html', color_roots=False)
    g.analysis_operator(9.876)
    g.show('iter.html', color_roots=False)
    g_copy.set_non_root_values_to_zero()
    g_copy.show('sosollessein.html', color_roots=False)


def line_test():
    g = non_reversible_graphs.DirectedLine(30)
    graph_list, modified_graph_list, q_list, q_prime_list=signal_processing.multi_resolution_and_reconstr(g)
    for g in modified_graph_list:
        g.show('g.html',color_roots=False)


if __name__ == '__main__':
    line_test()