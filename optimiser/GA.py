from math import cos, pi
from random import randint, uniform
import matplotlib.pyplot as plt
import numpy as np

p = 50
n = 20
g = 100

upperLimit = 100
lowerLimit = -100

class population():
    def __init__(self, individual):
        self.individual = individual
        self.pop = []
        self.fitness = 0
        self.gen = 0
        self.worst = self.individual()
        self.best = self.individual()
        self.best.inherit(np.full_like(np.arange(n), upperLimit,dtype=np.double))
        self.average = 0
        self.mutCount = 0

        for i in range(0,p):
            temp = self.individual()
            temp._randomise()
            print(temp)
            self.pop.append(temp)
            self.fitness = self.fitness + temp.fitness
            if temp.fitness > self.worst.fitness:
                self.worst = temp
            if temp.fitness < self.best.fitness:
                self.best = temp
        self.average = self.fitness/p


    def _selectIndiv(self):
        r1= randint(0, p-1)
        r2 = randint(0, p-1)
        print(r1,r2)
        if self.pop[r1].fitness < self.pop[r2].fitness:
            print(self.pop[r1].fitness, " is better than ", self.pop[r2].fitness)
            return self.pop[r1]
        else: 
            print(self.pop[r2].fitness, " is better than ", self.pop[r1].fitness)
            return self.pop[r2]

    
    def crossover(self):
        x = self._selectIndiv()
        y = self._selectIndiv()
        
        a = self.individual()
        b = self.individual() 

        upper = int(0.75*n)
        lower = int(0.25*n)
        crossPoint = randint(lower,upper)

        gene1 = []
        gene2 = []

        for i in range(0,crossPoint):
                gene1.append(x.gene[i])
                gene2.append(y.gene[i])
        for i in range(crossPoint,n):
                gene1.append(y.gene[i])
                gene2.append(x.gene[i])

        a.inherit(gene1)
        b.inherit(gene2)
        self._mutation(a)
        self._mutation(b)

        if a.fitness > self.newWorst.fitness:
            self.newWorst = a
        if self.newBest.fitness > a.fitness:
            self.newBest = a
        
        if b.fitness > self.newWorst.fitness:
            self.newWorst = b
        if self.newBest.fitness > b.fitness:
            self.newBest = b

        self.fitness = self.fitness + a.fitness + b.fitness
        
        self.newPop.append(a)
        self.newPop.append(b)
        print(a,b)

    def newGen(self):
        self.fitness = 0
        self.average = 0
        self.newBest = self.individual()
        self.newBest.inherit(np.full_like(np.arange(n), upperLimit,dtype=np.double))
        self.newWorst = self.individual()
        self.newPop = []
        
        for i in range(0,p,2):
            self.crossover()
        self.average = self.fitness/p

        for indiv in self.newPop:
            if indiv == self.worst:
                indiv = self.best

        print("Best: ", self.best)
        print("New Best: ", self.newBest)
        print("Worst: ", self.worst)
        print("New Worst: ", self.newWorst)

        self.worst = self.newWorst

        if self.best.fitness > self.newBest.fitness:
                self.best = self.newBest
                print("Best Changed")
        
        self.pop = self.newPop
        self.gen = self.gen + 1

    def _mutation(self, indiv):
        mutrate = randint(int(1/p*100),int(1/n*100))
        mutprob = randint(0,100)
        
        if mutrate > mutprob:
            r = randint(0,n-1)
            mutation= uniform(-0.4,0.4)
            newChromosome = indiv.gene[r] + mutation
            if newChromosome < lowerLimit or newChromosome > upperLimit:
                self._mutation(indiv)
            else: 
                self.mutCount = self.mutCount+1
                indiv.gene[r] = newChromosome

ppl = population()
bestArray = []
worstArray = []
avrgArray = []
genFitArray = []

print("Generation ", ppl.gen)
print("Best is ", ppl.best.fitness)
bestArray.append(ppl.best.fitness)
print("Worst is ", ppl.worst.fitness)
worstArray.append(ppl.worst.fitness)
print("Average is ", ppl.average)
avrgArray.append(ppl.average)

for i in range(1,g + 1):
    ppl.newGen()
    print("Generation ", ppl.gen)
    print("Best is ", ppl.best.fitness)
    bestArray.append(ppl.best.fitness)
    print("Worst is ", ppl.worst.fitness)
    worstArray.append(ppl.worst.fitness)
    print("Average is ", ppl.average)
    print("\n")
    avrgArray.append(ppl.average)
print(avrgArray)
print(bestArray)
fig, ax = plt.subplots()
print("Total mutations occured = ", ppl.mutCount)
print("Final Population Fitness:", ppl.fitness)
ax.plot(avrgArray, linewidth=2.0, label='Average')
ax.plot(bestArray, linewidth=2.0, label='Best')
ax. legend()
plt.show()                               
