# [QuBO for the TSP](../notebooks/tsp.ipynb) #

This notebook prepares a Hamiltonian for a randomly generated TSP problem.


```python
'''IMPORTS'''
import os;
import sys;

# NOTE: need this to force jupyter to reload imports:
for key in list(sys.modules.keys()):
    if key.startswith('src.'):
        del sys.modules[key];

os.chdir(os.path.dirname(_dh[0]));
sys.path.insert(0, os.getcwd());

from src.thirdparty.maths import *;
from src.thirdparty.plots import *;
from src.thirdparty.quantum import *;
from src.thirdparty.render import *;
from src.setup import *;
from src.api import *;

set_rng_seed(); # for repeatability
```


```python
n = 5;
prob_edge = 0.8;
E = [];
d = np.zeros(shape=(n, n), dtype=int);
for u in range(n):
    for v in range(u + 1, n):
        if np.random.rand() >= 1 - prob_edge:
            E.append((u, v));
            E.append((v, u));
            d[v, u] = d[u, v] = np.random.randint(0, 10);
fig = pgo.Figure(
    data = [
        pgo.Heatmap(
            z = d,
            x = list(range(n)),
            y = list(range(n)),
            xgap = 1,
            ygap = 1,
            colorbar_thickness = 20,
            colorbar_ticklen   = 3,
            showscale = False,
            colorscale = PLOTLY_COLOUR_SCHEME.GREYS.value,
        )
    ],
    layout = pgo.Layout(
        title = dict(
            text = f'Distance matrix',
            x = 0.5,
            y = 0.95,
            font = dict(
                family = 'monospace',
                size   = 18,
                color = 'rgba(0,100,255,1)',
            ),
        ),
        width           = 320,
        height          = 320,
        yaxis_autorange = 'reversed',
        showlegend      = False,
        xaxis_showgrid  = False,
        yaxis_showgrid  = False,
        xaxis = dict(visible = False),
        yaxis = dict(visible = False),
        margin = dict(l=20, r=20, t=60, b=20),
    )
);
display(fig);
```


```python
# Hamiltonian for minimisatoin of distances
H_B = np.zeros(shape=[n, n, n, n], dtype=int);
for (u, v) in E:
    for j in range(n):
        H_B[u, j, v, (j + 1) % n] = d[u, v];
H_B = H_B.reshape((n*n, n*n));
fig = pgo.Figure(
    data = [
        pgo.Heatmap(
            z = H_B,
            x = list(range(n*n)),
            y = list(range(n*n)),
            xgap = 1,
            ygap = 1,
            colorbar_thickness = 20,
            colorbar_ticklen   = 3,
            showscale = False,
            colorscale = PLOTLY_COLOUR_SCHEME.GREYS.value,
        )
    ],
    layout = pgo.Layout(
        title = dict(
            text = f'Hamiltonian H_B for minimisation of distances',
            x = 0.5,
            y = 0.975,
            font = dict(
                family = 'monospace',
                size   = 18,
                color = 'rgba(0,100,255,1)',
            ),
        ),
        width           = 640,
        height          = 640,
        yaxis_autorange = 'reversed',
        showlegend      = False,
        xaxis_showgrid  = False,
        yaxis_showgrid  = False,
        xaxis = dict(visible = False),
        yaxis = dict(visible = False),
        margin = dict(l=20, r=20, t=60, b=20),
    )
);
display(fig);
```


```python
H_A = np.zeros(shape=[n, n, n, n], dtype=int);
for u in range(n):
    for v in range(n):
        if (u, v) not in E:
            for j in range(n):
                H_A[u, j, v, (j + 1) % n] = 1;

for u in range(n):
    for i in range(n):
        for j in range(n):
            H_A[u, i, u, j] = 1;

for j in range(n):
    for u in range(n):
        for v in range(n):
            H_A[u, j, v, j] = 1;

H_A = H_A.reshape((n*n, n*n));
fig = pgo.Figure(
    data = [
        pgo.Heatmap(
            z = H_A,
            x = list(range(n*n)),
            y = list(range(n*n)),
            xgap = 1,
            ygap = 1,
            colorbar_thickness = 20,
            colorbar_ticklen   = 3,
            showscale = False,
            colorscale = PLOTLY_COLOUR_SCHEME.GREYS.value,
        )
    ],
    layout = pgo.Layout(
        title = dict(
            text = f'Hamiltonian H_B for path conditions',
            x = 0.5,
            y = 0.975,
            font = dict(
                family = 'monospace',
                size   = 18,
                color = 'rgba(0,100,255,1)',
            ),
        ),
        width           = 640,
        height          = 640,
        yaxis_autorange = 'reversed',
        showlegend      = False,
        xaxis_showgrid  = False,
        yaxis_showgrid  = False,
        xaxis = dict(visible = False),
        yaxis = dict(visible = False),
        margin = dict(l=20, r=20, t=60, b=20),
    )
);
display(fig);
```


```python
H = H_A + 0.1*H_B;
# print(np.abs(np.linalg.eigvals(H)));
fig = pgo.Figure(
    data = [
        pgo.Heatmap(
            z = H,
            x = list(range(n*n)),
            y = list(range(n*n)),
            xgap = 1,
            ygap = 1,
            colorbar_thickness = 20,
            colorbar_ticklen   = 3,
            showscale = False,
            colorscale = PLOTLY_COLOUR_SCHEME.GREYS.value,
        )
    ],
    layout = pgo.Layout(
        title = dict(
            text = f'Hamiltonian for problem',
            x = 0.5,
            y = 0.975,
            font = dict(
                family = 'monospace',
                size   = 18,
                color = 'rgba(0,100,255,1)',
            ),
        ),
        width           = 640,
        height          = 640,
        yaxis_autorange = 'reversed',
        showlegend      = False,
        xaxis_showgrid  = False,
        yaxis_showgrid  = False,
        xaxis = dict(visible = False),
        yaxis = dict(visible = False),
        margin = dict(l=20, r=20, t=60, b=20),
    )
);
display(fig);
```
