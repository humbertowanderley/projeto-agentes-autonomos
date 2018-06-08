# Projeto de Agentes Autônomos

Documentação do projeto da disciplina de agentes autônomos.
**Equipe:**



## Instalando a API
* Instale o python versão 3.6.5
* Certifique-se que você tem o pip instalado.
* No terminal (linux/mac) ou powershell (windows), instale a api de Starcraft 2 
```bash
	pip install sc2
```
* Para rodar o agente-exemplo da estratégia **(mybot.py)**, deve-se utilizar um dos comando abaixo:
```bash
	python .\mybot.py
```

```bash
	python3 .\mybot.py
```

## Estratégia Básica
**Raça:** Protoss

A estratégia principal consiste em localizar a base inimiga o mais rápido possível (exploração dos possíveis pontos do mapa onde podem haver inimigos), construir alguns pilares de **proxy** (ato de colocar pontos de teleporte próximos a base inimiga) e começar a teleportar **Dark Templars** (unidades invisíveis) antes do inimigo ter tempo hábil pra evoluir.
- O que pode dar errado e como contornar?
	1.	O inimigo localizar os pylon e destruí-los:
		- Novos **pylons** devem ser construídos em locais randômicos próximos a base inimiga para garantir que sempre hajam **pylons** disponíveis para teleportar os **Dark Templars**.
	2. O inimigo ter unidades/construções que podem ver coisas invisívels ( sentry, missile turrents, oversees, phanton cannons, etc):
		*	Deve-se enviar vários **Stalkers** para destruir essas unidades/construções e em seguida atacar com os **Dark Templars**.
	3. O inimigo tentar atacar com um rush inicial: 
		- Deve haver sempre um grupo de **Stalkers** e **Dark Templars** próximo a base e suas expansões para defender.
	4. Inimigo ter ataque aéreo:
		-	O ideal é o jogo não chegar a esse ponto, mas se o inimigo ter naves, deve-se defender com os **Stalkers**, que podem atacar alvos aéreos.

- **Ordem de construções:**

	 1. Pylon:  ![Pylon](https://liquipedia.net/commons/images/8/83/Techtree-building-protoss-pylon.png)
	 2. Gateway:  ![Gateway](https://liquipedia.net/commons/images/b/b6/Techtree-building-protoss-gateway.png)
	 3. Cybernetics Core:  ![Cybernetics Core](https://liquipedia.net/commons/images/9/9f/Techtree-building-protoss-cyberneticscore.png)
	 4. Twilight Council:  ![Twilight Council](https://liquipedia.net/commons/images/0/03/Techtree-building-protoss-twilightcouncil.png)
	 5. Dark Shrine:  ![Dark Shrine](https://liquipedia.net/commons/images/6/64/Techtree-building-protoss-darkshrine.png)

- **Unidades**
Probe: ![Probe](https://liquipedia.net/commons/images/thumb/c/c9/Techtree-unit-protoss-probe.png/25px-Techtree-unit-protoss-probe.png) Stalker: ![Stalker](https://liquipedia.net/commons/images/thumb/c/cb/Techtree-unit-protoss-stalker.png/25px-Techtree-unit-protoss-stalker.png) Dark Templar: ![Dark Templar](https://liquipedia.net/commons/images/thumb/c/c0/Techtree-unit-protoss-darktemplar.png/25px-Techtree-unit-protoss-darktemplar.png)

- **Tecnologias**
Warp Gate: ![Warp Gate](https://liquipedia.net/commons/images/thumb/d/d2/Techtree-building-protoss-warpgate.png/25px-Techtree-building-protoss-warpgate.png)

## Agentes
A estratégia será implementada através de uma abordagem multi agentes. Cada um dos agentes se comunicará com os demais através de memória compartilhada. Basicamente será uma lista acessível por qualquer um dos agentes. A lista descreve informações interessantes sobre o estado atual da estratégia, possibilitando a tomada de decisão do que deve e quando deve ser feito.

 **Tabela de memória compartilhada**
|	Informação			|  Tipo			| Inicialização	|	Objetivo
|---------------------------------------|-----------------------|---------------|----------------|
|  Gateways Construídos			| Inteiro 		| 0		| 6
|  Cybernetics Core Construídos		| Inteiro 		| 0		| 1
|  Twilight Council Construídos 	| Inteiro 		| 0		| 1
|  Dark Shrine Council 			| Inteiro 		| 0		| 1
|Nexus Ativos 				| Inteiro 		| 1 		| 3
|Stalkers Pelotão de Ataque 		| Inteiro 		| 0 		| 30
|Dark Templars Pelotãao de Ataque 	| Inteiro 		| 0 		| 5
|Stalkers Pelotão de Defesa 		| Inteiro 		| 0 		| 15
|Dark Templars Pelotão de Defesa 	| Inteiro 		| 0 		| 2
|Pilows de proxy 			| lista com localização | 0 		| 5


### Agente de Exploração
Encarregado de explorar o mapa com o objetivo de descobrir onde a base inimiga está o mais rápido possível.
-	Se o explorador dor atacado, ele deve tentar sobreviver fugindo, e depois continuar sua exploração.
-	Se o explorador morrer, deve-se alocar outro, até a base inimiga ser descoberta.
-	Deve Construir e Manter os pylon de proxy prem locais randomicos próximo  a base inimiga quando o agente estrategista solicitar.

### Agente Administrador de Recursos
Encarregado de garantir uma coleta de recursos inteligente, não sobrecarregando os nexus com trabalhadores em exesso e expandindo sempre que possível para novas áreas. O ideal é limitar o número máximo de trabalhadores toal em até 40 para evitar afetar slots destinados a unidades de combate.

- Recursos a serem gerenciados:
	* **Minerais:** Sempre que necessário, fazer **expansões**, garantindo o aumento de produção de minerais sem afetar a estratégia básica.
	* **Gás Vespene:** Sempre construir assimiladores nos **Vespene Geysers** próximos aos **Nexus** e alocar trabalhadores
	* **Capacidade Populacional:** Sempre garantir a capacidade de aumentar a população construindo **pylons** quando o limite estiver próximo de ser atingido.

### Agente de Construção
O agente deve garantir a construção de todos os **buildings** necessários para a criação dos **Dark Templars** o mais rápido possível.

 - O agente é encarregado de autorizar o Agente de recursos a expandir.
 - O agente deve garantir a correta ordem de construção dos buildings da estratégia.
 - O agente deve reconstruir algum **building** da estratégia caso ele seja destruído.
 - O agente deve garantir a finalização da pesquisa dos **Warp Gate**
 - O agente deve aprimorar alguns Gateway em Warp Gates.

### Agente Militar de Defesa
Deve garantir a defesa da base e suas expansões, sempre ficando próximo a elas e respondendo a possíveis ataques.

 - O agente deve sempre ter um pelotão de defesa com um número pré definido de Stalkers e alguns poucos **Dark Templars** prontos para defender.
 - O agente deve controlar a patrulha do pelotão entre a base e suas **expansões**.
 -  O agente deve solicitar ajuda ao Agente estrategista caso ele esteja próximo de ser derrotado.

### Agente Militar de Ataque
Deve orquestrar  pelotões de ataque com Transdobra de Dark Templars combinado com um pelotão de Stalkers.

 - O agente tem que sempre manter um **número mínimo** de unidades de ataque, repondo-as quando morrerem.
 - O agente deve ser capaz de enviar pelotões de **Stalkers** para destruir unidades que detectem os **Dark Templars** quando solicitado pelo agente estrategista.
 - O agente deve **patrulhar** as regiões próximas a base inimiga e destruir exploradores inimigos que estejam tentando encontrar a sua base.
 - O agente deve socorrer o agente de defesa caso ordenado pelo estrategista.

### Agente Estrategista
Deve solicitar a colocação de um número pré definido de pylons de proxy próximo a base inimiga logo quando ela for descoberta e os dark templar's estiverem próximos de serem criados.

 - O Agente deve garantir a reposição de **pylons** de **proxy** por parte do agente de exploração em posição aleatória próximo a base inimiga sempre que algum **pylon** de proxy for destruído.
 - O agente deve informar ao agente militar de ataque quando deve parar o ataque de **Dark Templars** devido a detecção de unidades invisíveis por parte do inimigo, e solicitar o ataque de **Stalkers** priorizando as unidades inimigas que detectam os **Dark Templars**. 
 - O agente deve mandar o Agente Militar de ataque ajudar o Agente Militar de defesa caso ele esteja sendo derrotado

### Agente Principal
É responsável pela criação da memória compartilhada e por instanciar todos os outros agentes. 

### Hierarquia dos Agentes
Estrategista pode dar ordens ao Explorador
Estrategista pode dar ordens ao Militar de ataque
Coletor de recursos é independente
Construtor é independente
Militar de Defesa pode dar ordens ao Estrategista
Agente principal instancia todos os outros agentes.

## Relatório
O Relatório do projeto deve ser elaborado a medida que os agentes forem ficando prontos e documentados no github. A documentação deve ser feita a medida que os micro objetivos dos agentes estejam sendo concluídos.

## Divisão do Projeto

**Isaac:** Agente de Exploração

**Bruno:** Agente Militar de Defesa

**Diogo:** Agente Administrador de Recursos

**Leandro:** Agente Militar de Ataque

**Well:** Agente de Construção

**Humberto:** Agente principal e Agente Estrategista

**Carol:** Relatório

## Considerações Finais

- Qualquer parte da documentação inicial está sujeita a alteração.
- A memória compartilhada pode ter mais ou menos informações, conforme vá havendo necessidade por parte dos agentes durante a implementação.
- A pasta basic bot é apenas um esboço simples de um único agente do que deve ser a estratégia. Ele tem muitas limitações e alguns bugs, porém pode ajudar na implementação dos agentes e no entendimento da estratégia na prática.
- Cada agente deve ser criado em um arquivo separado dentro da pasta Agentes. Ao final será dado um import de todos os agentes no arquivo do agente principal para o instanciamento.

**Deadline da implementação: 01/07/2018**
