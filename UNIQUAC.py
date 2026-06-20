##UNIQUAC
import numpy as np
import pandas as pd
from openpyxl import load_workbook
from scipy.optimize import minimize

"""
dados = np.array([
    [[1, 1.9031, 1.728],
     [1, 0.9011, 0.848],
     [1, 0.6744, 0.540]],

    [[1, 1, 1.2],
     [2, 0.9011, 0.848],
     [1, 0.6744, 0.540]]])

divisão em dois arrays, um por composto, cada array é composto por arrays de todas 3 funções orgânicas que apresentam na ordem [nu, R, Q]

"""

def UNIQUAC(Temp, x, dados, u, Antoine, z=10):
    R_cte=8.314 #J/mol.K
    T = Temp[0]
    erro=1

    dados=np.array(dados)
    nu=dados[:,:,0]
    R=dados[:,:,1]
    Q=dados[:,:,2]
    u=np.array(u)

    Antoine=np.array(Antoine)

    #Cálculo r e q
    r = []
    q = []
    for i in range(len(x)):
        r_i = sum(nu[i][j]*R[i][j] for j in range(len(R)))
        q_i = sum(nu[i][j]*Q[i][j] for j in range(len(Q)))
        r.append(r_i)
        q.append(q_i)

    #Cálculo de theta
    theta = []
    for i in range(len(x)):
        theta_i = (q[i]*x[i])/sum(q[j]*x[j] for j in range(len(x)))
        theta.append(theta_i)

    #Cálculo de phi
    phi = []
    for i in range(len(x)):
        phi_i = (r[i]*x[i])/sum(r[j]*x[j] for j in range(len(x)))
        phi.append(phi_i)

    #Cálculo de l
    l = []
    for i in range(len(x)):
        l_i = (z/2)*(r[i]-q[i])-(r[i]-1)
        l.append(l_i)

    #Cálculo do parâmetro b
    b_12 = T**2*u[0][0]+T*u[0][1]+u[0][2]
    b_21 = T**2*u[1][0]+T*u[1][1]+u[1][2]
    b=[[0,b_12],[b_21,0]]

    #Cálculo de tau
    tau = []
    for i in range(len(x)):
        tau_i = []
        for j in range(len(x)):
            tau_ij = np.exp(-b[i][j]/T)
            tau_i.append(tau_ij)
        tau.append(tau_i)

    #Cálculo de ln(gamma)
    ln_gamma_res = []
    for i in range(len(x)):
        sumln = sum(theta[j]*tau[j][i] for j in range(len(x)))
        sumdup = sum(theta[j]*tau[i][j]/(sum(theta[k]*tau[k][j] for k in range(len(x)))) for j in range(len(x)))
        ln_gamma_res_i = q[i]*(1 - np.log(sumln) - sumdup)
        ln_gamma_res.append(ln_gamma_res_i)
    ln_gamma_comb = []
    for i in range(len(x)):
        ln_gamma_comb_i = np.log(phi[i]/x[i]) + (z/2)*q[i]*np.log(theta[i]/phi[i]) + l[i] - (phi[i]/x[i])*sum(x[j]*l[j] for j in range(len(x)))
        ln_gamma_comb.append(ln_gamma_comb_i)
    ln_gamma = [ln_gamma_comb[i] + ln_gamma_res[i] for i in range(len(x))]

    #Cálculo dos y
    y = []
    for i in range(len(x)):
        y_i = x[i]*np.exp(ln_gamma[i])*10**(Antoine[i][0] - Antoine[i][1]/(T + Antoine[i][2]))
        y.append(y_i)

    #Cálculo do erro
    erro = abs(y[0]+y[1] - 1)
    return erro, y

#salvar valores de x1=0 como o mesmo da solução ideal calculado no Excel
x_lista=[[0,1]]
y_lista = [[0,1]]
T_lista = [354.2795901]
erro_lista = [0]
#iterar para todos x
for i in np.arange(0.01,1.0,0.01):
    #crio o param x[x1,x2], muda a cada iteração de 0.01 até 0.99 de 0.01 em 0.01
    x=[i, 1-i]

    #crio o param dados: componente 1 e param das suas funções e o mesmo para comp 2, cada lista é [nu, R, Q]
    dados = np.array([
        [[1, 1.9031, 1.728],
        [1, 0.9011, 0.848],
        [1, 0.6744, 0.540]],

        [[1, 1, 1.2],
        [2, 0.9011, 0.848],
        [1, 0.6744, 0.540]]])
    
    #crio o param u[[tau11, tau12],[tau21, tau22]]
    u=np.array([[-0.0247125,19.76618875,-3709.242035],[0.0205125,-16.53772875,3204.29406]])

    #crio o param Antoine[[A1, B1, C1],[A2, B2, C2]]
    Antoine = np.array([[4.22809,1245.7,-55.189], [4.57795,1221.42,-87.474]])

    #objetivo
    def objective(Temp, x, dados, u, Antoine, z=10):
        obj = UNIQUAC(Temp, x, dados, u, Antoine, z=10)
        return obj[0]

    #itero em Temp tendo dado os argumentos até erro <= 1e-10 com método Nelder-Mead
    resultado = minimize(objective, 298.15, args=(x, dados, u, Antoine), tol=1e-6, method='Nelder-Mead')
    #retorno UNIQUAC utiilizando o último T da minimização
    fim = UNIQUAC(resultado.x,x,dados,u,Antoine)
    #salvo os valores de x, y, T e erro em listas para cada valor de x
    x_lista.append(x)
    y_lista.append(fim[1].copy())
    T_lista.append(resultado.x[0])
    erro_lista.append(fim[0].copy())

#salvar valores de x1=1 como o mesmo da solução ideal
x_lista.append([1,0])
y_lista.append([1,0])
T_lista.append(349.8142322)
erro_lista.append(0)

#organizo as colunas x1, x2, y1 e y2
col_A = [x[0] for x in x_lista]
col_B = [x[1] for x in x_lista]
col_C = [y[0] for y in y_lista]
col_D = [y[1] for y in y_lista]

#salvo as colunas com títulos
data = {
    'x1': col_A,
    'x2': col_B,
    'y1': col_C,
    'y2': col_D,
    'T (K)': T_lista,
    'erro': erro_lista
}

#crio arquivo chamado UNIQUAC com todos dados em colunas
df = pd.DataFrame(data)
df.to_excel('UNIQUAC.xlsx',index=False)



