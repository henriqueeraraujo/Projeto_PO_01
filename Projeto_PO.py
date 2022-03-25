#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  8 10:49:11 2021

@author: henrique
"""

import gurobipy as gp
from gurobipy import *
from math import dist




def le_dados (nome_arq):
    with open (nome_arq, "r") as f:
        linhas = f.readlines()
        valores = linhas[0].strip().split(" ")
        paradas = int(valores[0])
        estudantes = int(valores[2])
        rotas = int(valores[4])
        dist_max = float(valores[6])
        capacidade = int(valores[9])

        rotulos_vertices = list()
        #cria rótulos das paradas
        for i in range(paradas):
            rotulo = "Parada_{}".format(i)
            rotulos_vertices.append(rotulo)
        #cria rótulos dos estudantes
        for i in range(estudantes):
            rotulo = "Estudante_{}".format(i+1)
            rotulos_vertices.append(rotulo)
        #cria rótulos dos estudantes
        for i in range(rotas):
            rotulo = "Rota_{}".format(i+1)
            rotulos_vertices.append(rotulo)
       
        
        nodes = rotulos_vertices
        #cria a matriz das coordenadas
        coordenadas = [[0 for x in range(2)] for y in range(paradas+estudantes)]
        
        del(linhas[0],linhas[0])
      
            
        #preenchendo os valores das coordenadas X e Y das paradas
        for i in range(paradas):
            valores = linhas[0].strip().split(" ")
            coordenadas[i][0] = float(valores[1])
            coordenadas[i][1] = float(valores[2])
            del(linhas[0])
            
        #deletando os espaçoes vazios
        del(linhas[0],linhas[0])
        
        
        #preenchendo os valores das coordenadas X e Y dos estudantes
        for i in range(estudantes):
            valores = linhas[0].strip().split(" ")
            coordenadas[i+paradas][0] = float(valores[1])
            coordenadas[i+paradas][1] = float(valores[2])
            del(linhas[0])
        
        arcs_aux = tuple()
        arcs = gp.tuplelist()
        capacity = dict()
        cost = dict()
       
        #montando dicionários de arcos entre alunos e paradas
        for i in range (estudantes):
            for l in range (1, paradas):
                distancia = dist(coordenadas[paradas+i],coordenadas[l])
                if distancia <= dist_max :
                    rotulo_1 = nodes[paradas+i]
                    rotulo_2 = nodes[l]
                    arcs_aux = (rotulo_1, rotulo_2)
                    arcs.append(arcs_aux)
                    capacity[arcs_aux] = 1
                    cost[arcs_aux] = distancia
                    
        del(linhas[0],linhas[0])
     
        #montando dicionários de arcos entre paradas e rotas
        for i in range(rotas):
            valores = linhas[0].strip().split(" ")
            parada_rota = int(valores[1])
            rotulo_1 = nodes[parada_rota]
            rotulo_2 = nodes[paradas+estudantes+i]
            arcs_aux = (rotulo_1, rotulo_2)
            arcs.append(arcs_aux)
            capacity[arcs_aux] = capacidade
            cost[arcs_aux] = 0
            del(linhas[0])
            for l in range(2, paradas):
                parada_rota = int(valores[l])
                if parada_rota == 0 :
                    break
                rotulo_3= nodes[parada_rota]
                rotulo_2 = nodes[paradas+estudantes+i]
                arcs_aux= (rotulo_3, rotulo_2)
                
                arcs.append(arcs_aux)
                capacity[arcs_aux] = capacidade
                cost[arcs_aux] = 0
               
        
        #dicionario de demandas
        inflow = dict()
        
        demanda = capacidade * rotas
        demanda0 = demanda - estudantes
        
        #se o número de alunos for inferior a capacidade das rotas
        if estudantes < demanda :
            inflow[nodes[0]]= demanda0
            for i in range(1, paradas):
                inflow[nodes[i]] = 0
      
        if estudantes == demanda :
            for i in range(paradas):
                inflow[nodes[i]] = 0
        
        for i in range(estudantes):
                inflow[nodes[i+paradas]] = 1
        for i in range(rotas):
                inflow[nodes[i+paradas+estudantes]] = -capacidade
      
        
    
        m = Model('netflow')
      
        #criando variáveis 
        flow = {}
        for i,j in arcs:
            flow[i,j] = m.addVar(ub=capacity[i,j], obj=cost[i,j],
                                      name='flow_%s_%s' % (i, j))
    
        #definição da função objetivo
        m.setObjective(quicksum(flow[i,j] * cost[i,j] for i, j in arcs), sense = gp.GRB.MINIMIZE)
        
        m.update()
       
        #restrções de fluxo máximo
        for i,j in arcs:
           m.addConstr(flow[i,j] <= capacity[i,j],
               'cap_%s_%s' % (i, j))
           m.addConstr(flow[i,j] >= 0,
               'cap_%s_%s' % (i, j))
        
        #restrições de conservação de fluxo
        for j in nodes:
           m.addConstr(
               quicksum(flow[i,j] for i,j in arcs.select('*',j)) +
                   inflow[j] ==
                quicksum(flow[j,k] for j,k in arcs.select(j,'*')),
                  'node_%s' % (j))
               
        m.optimize()
    
        if m.status == GRB.Status.OPTIMAL:
            solution = m.getAttr('x', flow)
            for i,j in arcs:
                if solution[i,j] > 0:
                    print('%s -> %s: %g' % (i, j, solution[i,j]))
        
    
arquivo = "Instancias_Trabalho1/inst49-1s20-100-c25-w5.coord"
le_dados(arquivo)