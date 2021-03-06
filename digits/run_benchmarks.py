import itertools
import math
import random
import timeit
import numpy as np
import pandas as pd
import plotly_express as px
import plotly as py
import plotly.graph_objs as go
from plotly.subplots import make_subplots

np.set_string_function(lambda a: str(a.shape), repr=False)
np.random.seed(1)


def run_benchmarks(make_nn_fn, train_nn_fn, eval_nn_fn, load_data_fn, all_hparams):
    print('Loading data...')
    eval_results = []
    labels = []
    runtimes = []
    test_accs = []
    for hparams in all_hparams:
        tr_d, va_d, te_d = load_data_fn(hparams)

        nn = make_nn_fn(tr_d, **hparams)

        def _benchmark_training():
            accuracies, costs = train_nn_fn(nn, tr_d, va_d)
            eval_results.append(dict(epoch=list(range(len(costs))),
                                     cost=costs, acc=accuracies))

        unique_params = {k: v for k, v in hparams.items()
                         if len(list(set(d[k] for d in all_hparams))) > 1}
        label = ', '.join(f'{k}: {v}' for k, v in unique_params.items())
        labels.append(label)

        time = timeit.timeit(lambda: _benchmark_training(), number=1)
        runtimes.append(time)

        # Evaluating on test data:
        test_acc = eval_nn_fn(nn, te_d)
        test_accs.append(test_acc)

        print(f'Finished running with params {label}, run time: {time:.1f}, '
              f'test data accuracy: {test_acc}')
        print()

    common_params = {k: v for k, v in all_hparams[0].items()
                     if len(list(set(d[k] for d in all_hparams))) == 1}
    common_params = [f'{k}: {v}' for k, v in common_params.items()]

    # df = pd.DataFrame(dict(epoch=[], cost=[], acc=[], key=[]))
    # for res in eval_results:
    #     df = df.append(pd.DataFrame(res))
    # px.line(df, x='epoch', y='acc', color='key', title=', '.join(common_params))

    fig = make_subplots(rows=2, cols=1,
                        subplot_titles=[', '.join(common_params), 'Run times'],
                        row_heights=[3, 1])
    for label, res in zip(labels, eval_results):
        fig.add_scatter(x=res['epoch'], y=res['acc'], name=label, mode='lines+markers',
                        row=1, col=1)
    fig.add_bar(x=labels, y=runtimes, row=2, col=1, )
    py.offline.plot(fig)

    # Y_classes, train, test, valid = load_toy()
    # hidden_layers = [8]
    # epochs = 30
    # learning_rate = 3.0
    # batch_size = 10
    # show_images(get_X(train), get_Y(train))

    # show_images(nn.weights[0][0:9,:].T)
    #
    # # show average of all weights of first layer
    # w_784_10 = np.dot(nn.weights[0].T + nn.biases[0].T, nn.weights[1].T) + nn.biases[1].T
    # show_images(w_784_10)
    #
    # # train on digit 1 and show weights that are activated highly:
    # As, Zs = nn.feedforward(get_X(train)[:,0:1])
    # ws = nn.weights[0][np.where(np.round(As[-2]*1000) >= 1000, 1, 0)[:,0],:]
    # # we.shape == (784, number-of-images)
    # show_images(ws.T)
    # # show 4th image (a 3)
    # show_images(get_X(train)[:,3:4])


def show_images(X, Y=None, cols=3):
    # X.shape == (pixels, images)
    datas = X.T
    cmaps = itertools.repeat('Reds')
    if Y is not None:
        if len(Y.shape) > 1 and Y.shape[0] > 1:
            Y = np.argmax(Y, axis=0)  # convert to the flat shape
        cmaps = np.where(Y == 1, 'Greens', 'Reds')
        cmaps = cmaps.reshape((X.shape[1]))

    rows = math.ceil(len(datas) / cols)
    fig, axes = plt.subplots(rows, cols)
    axes = axes.reshape((rows, cols))
    for i, (x, cm) in enumerate(zip(datas, cmaps)):
        i, j = i//cols, i%cols
        width = math.ceil(math.sqrt(x.shape[0]))
        plt.axis('off')
        axes[i, j].get_xaxis().set_visible(False)
        axes[i, j].get_yaxis().set_visible(False)
        axes[i, j].imshow(x.reshape((width, width)), cmap=cm)
    plt.show()


def show_weights(nn, layer_n=1):
    second_layer = nn.weights[layer_n-1]  # (k, j)
    show_images(second_layer.T)


def explore_0layer_nn(test_data, nn):
    # accuracy for each digit type
    plots = []
    for i in range(10):
        y = binary_arrays_to_digits(get_Y(test_data))
        yi = y[y == i]
        x = get_X(test_data).T
        xi = x[y == i].T
        predictions = nn.predict(xi)
        acc = sum(int(p == t) for p, t in zip(predictions, yi)) / len(yi)
        print(f"Accuracy for digit {i}: {acc}")

        # plottoing for 1 example
        test_digit = xi[:,i:i+1]
        As, Zs = nn.feedforward(test_digit)
        weight = np.mean((As[-1] * nn.weights[0]).T, axis=1).reshape((xi.shape[0],1))
        plots.extend([test_digit, weight])

    show_images(np.concatenate(plots, axis=1), cols=4)




