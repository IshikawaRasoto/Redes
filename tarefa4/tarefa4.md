# Trabalho VLAN. - Trabalho 4.
---

> **Dica: Antes de fazer a tarefa**, assista aos dois videos tutoriais:
> 1. [Tutorial 1](https://www.youtube.com/watch?v=H01eZjdcHTo)
> 2. [Tutorial 2](https://www.youtube.com/watch?v=_taHFD9zDiA)

> **Dica: Antes de fazer a tarefa**, instale o Packet tracer:
> 1. [BLOG LAB CISCO](http://labcisco.blogspot.com.br/p/laboratorios.html)
> 2. [PACKET TRACER NETWORK](http://www.packettracernetwork.com/)
> 3. [APLICATIVO PACKET TRACER](https://www.baixaki.com.br/download/packet-trace.htm)

> **Importante:** **Os exercícios a seguir serão realizados com o simulador Packet Tracer da Cisco.**
> 1. Entre no simulador e faça os dois exercícios a seguir.

# Exercício: Parte 1

![Topologia VLAN 1](/maurofonseca/lib/exe/fetch.php?media=cursos:icsr30:vlan1.jpg)

1. Divida o switch em 2 VLANs.
   * Professores: **VLAN 1** (portas 1 e 2)
   * Alunos: **VLAN 2** (portas 3 e 4)
   * Faça as VLANS se comunicarem entre si. 
     * Teste utilizando o *ping* para verificar a comunicação entre máquinas:
       * VLAN1 com VLAN1 (funciona)
       * VLAN1 com VLAN2. (Não Funciona)

> **Importante:**
> * Entregue o exercício **com todos os comandos usados na ordem e comentados**.

# Exercício: Parte 2

![Topologia VLAN 2](/maurofonseca/lib/exe/fetch.php?media=cursos:icsr30:vlan2.jpg)

1. Divida os switch em 2 VLANs.
   * Professores: **VLAN 1** (portas 1 e 2)
   * Alunos: **VLAN 2** (portas 3 e 4)
   * Faça os switches se comunicarem através de uma porta Trunk (Sem roteador.)
     * Teste utilizando o *ping* para verificar a comunicação entre máquinas:
       * VLAN1 com VLAN1 (No mesmo switch)( Comunica)
       * VLAN1 com VLAN2 (No mesmo switch)(Não Comunica)
       * VLAN1 com VLAN1 (Em switchs diferentes)(Comunica)
       * VLAN1 com VLAN2 (Em switchs diferentes)(Não Comunica)    
   * Faça as VLANS se comunicarem através de um roteador
     * Teste utilizando o *ping* para verificar a comunicação entre máquinas:
       * VLAN1 com VLAN1 (No mesmo switch)( Comunica)
       * VLAN1 com VLAN2 (No mesmo switch)( Comunica)
       * VLAN1 com VLAN1 (Em switchs diferentes)( Comunica)
       * VLAN1 com VLAN2 (Em switchs diferentes)( Comunica)

> **Importante:**
> * Entregue o exercício **com todos os comandos usados na ordem e comentados** em um arquivo pdf.

> **Dica:** Lembre-se: Este exercicio não precisa de apresentação.