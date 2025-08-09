# **RepackerMS \- Mod Tool for Yakuza Games**

This tool provides a workaround for installing mods in certain Yakuza games purchased from the Microsoft Store or played via Xbox Game Pass, where the Shin Ryu Mod Manager is not functional. This is the only known method to get mods working for games like **Yakuza Kiwami 2** and **Like a Dragon Pirate Yakuza.**

The tool also works for Steam versions, but it's generally recommended for Steam users to use SRMM, as this tool is intended as a "hard" manual installation method.

### **Requirements**

* **Python 3:** The script itself requires Python 3 to run.  
* [**ParTool.dll**](https://www.google.com/search?q=https://github.com/Kaplas/ParTool)**:** This is the core tool used for repacking the game's `.par` files. You must place the `ParTool.dll` file in a subfolder named `partool` within the same directory as this script.  
* [**.NET Desktop Runtime**](https://dotnet.microsoft.com/download/dotnet/6.0)**:** `ParTool.dll` is a .NET application, so you must have the .NET runtime installed on your system to run it.

### **How to Use**

1. **Prepare your mods:** Unpack your mod files into a structured folder. The most crucial part is to have your mod files organized within a subfolder named data. This data folder should be the one you point the tool to.  
   **Example structure:**  
   /Mod/  
   └─── data/  
        └─── talk\_spr/  
             └─── texture/  
                  └─── modded\_file.dds

2. **Launch the RepackerMS GUI.**  
3. **Select MOD Folder:** In the GUI, select the folder that contains your modded data directory. For the example above, you would select /MyAwesomeMod/.  
4. **Select Game Folder:** Select the game's main media directory. This path is where all the .par files are located.  
   Example path for MS Store/Xbox Games:  
   C:\\XboxGames\\Like a Dragon- Pirate Yakuza in Hawaii\\Content\\runtime\\media  
5. **Choose Compression Mode:**  
   * **1 (Default):** Use this for normal gameplay. It applies the standard SLLZ compression, which is how the game expects its files. This prevents performance issues.  
   * **0:** Use this for uncompressed files. This is useful for debugging and rapid testing, but can cause a significant performance drop (lower framerate) in the game due to larger file sizes and increased I/O load.  
6. **Click "Start"** to begin the repacking process. The tool will automatically create a backup of the original .par files before repacking them with your modded files.

# **RepackerMS \- Ferramenta de Mod para Jogos Yakuza**

Esta ferramenta oferece uma solução para instalar mods em certos jogos Yakuza comprados na Microsoft Store ou jogados via Xbox Game Pass, onde o Shin Ryu Mod Manager não funciona. Este é o único método conhecido para fazer mods funcionarem em jogos como **Yakuza Kiwami 2** e **Like a Dragon: Infinite Wealth**.

A ferramenta também funciona para versões da Steam, mas geralmente é recomendado que os usuários da Steam usem gerenciadores de mod dedicados, pois esta ferramenta é uma forma de instalação manual "hard".

### **Como Usar**

1. **Prepare seus mods:** Descompacte os arquivos do seu mod em uma estrutura de pastas organizada. A parte mais importante é ter seus arquivos de mod dentro de uma subpasta chamada data. Esta pasta data é a que você deve apontar na ferramenta.  
   **Estrutura de exemplo:**  
   /MeuModIncrível/  
   └─── data/  
        └─── talk\_spr/  
             └─── texture/  
                  └─── modded\_file.dds

2. **Inicie a GUI do RepackerMS.**  
3. **Selecione a Pasta do MOD:** Na GUI, selecione a pasta que contém o seu diretório data modificado. Para o exemplo acima, você selecionaria /MeuModIncrível/.  
4. **Selecione a Pasta do Jogo:** Selecione o diretório de mídia principal do jogo. Este caminho é onde todos os arquivos .par estão localizados.  
   Caminho de exemplo para jogos MS Store/Xbox:  
   C:\\XboxGames\\Like a Dragon- Pirate Yakuza in Hawaii\\Content\\runtime\\media  
5. **Escolha o Modo de Compressão:**  
   * **1 (Padrão):** Use para jogabilidade normal. Aplica a compressão SLLZ padrão, que é a forma como o jogo espera seus arquivos. Isso evita problemas de desempenho.  
   * **0:** Use para arquivos sem compressão. Isso é útil para depuração e testes rápidos, mas pode causar uma queda significativa de desempenho (taxa de quadros mais baixa) no jogo devido ao tamanho maior dos arquivos e ao aumento da carga de E/S (leitura/gravação).  
6. **Clique em "Iniciar"** para começar o processo de repack. A ferramenta criará automaticamente um backup dos arquivos .par originais antes de reempacotá-los com os arquivos do seu mod.