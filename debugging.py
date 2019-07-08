from library import *
import pandas as pd

threshold = 0.09

df_data = pd.DataFrame(np.random.randn(100, 4),
                       columns=['A', 'B', 'C', 'D'])
lol = df_data.values.tolist()

correlation_matrix = df_data.corr()

print(correlation_matrix)
# df_data.plot()
# plt.show()
#
# create dictionary to keep indices
A = correlation_matrix.values.tolist()
B = {i: A[i] for i in range(len(A))}
# sort lines in a decent order by the sum of their elements // by their correlation with each other
C = dict(sorted(B.items(), key=lambda i: sum([abs(x) for x in i[1]]), reverse=True))

print(C)
i_stored = []

corr_coded_tricklets = {}
atoms_coded_tricklets = {}

# for each line (TS)
for k, X in C.items():
    # Find the index maximizing the correlation
    # m <=  list of indices of corr TS candidates AND
    #       already stored normally and different than itself
    m = [v for i, v in enumerate(X) if (
            i in i_stored and abs(v) >= abs(threshold) and k != i)]
    i_m = [i for i, j in enumerate(X) if m and j == max(m)]  # indice of the max

    if i_m:  # store corr
        i_m = i_m[0]
        x = lol[i_m]
        y = lol[k]
        corr_coded_tricklets[k] = i_m, shift_mean(x, y)

    else:  # store sparse
        atoms_coded_tricklets[k] = lol[k]
    i_stored.append(k)  # add k to the list of elements stored in sparse way

print(atoms_coded_tricklets)
print(corr_coded_tricklets)
print()

for k, v in atoms_coded_tricklets.items():
    print(v)
    plt.plt(v)

plt.show()
