# SMN-Tubes-IF2224

> Tugas Besar - IF2224 Teori Bahasa Formal dan Otomata 2025

<h3 align="center">SayMyName (SMN)</h3>
<p align="center">
    Pascal-S Compiler and Interpreter
    <br />
    <br />
    <a href="https://github.com/Kurondt/SMN-Tubes-IF2224/releases/">Releases</a>
    ·
    <a href="./doc/">Project Report and Documentation</a>
</p>

## Table of Contents <a name="table-of-contents"></a>

- [About](#about)
- [Requirement](#requirement)
- [Installation and Usage](#installation-and-usage)
- [Task Distribution](#task-distribution)

---

## About <a name="about"></a>

<div align="right">(<a href="#table-of-contents">back to top</a>)</div>

<p align="justify">This project is a milestone project of 2025 IF2224 Formal Language and Automata Theory course at <a href="https://itb.ac.id" target="_blank">Institut Teknologi Bandung</a>.</p>

<p align="justify">This project develops a compiler and interpreter for the Pascal-S programming language. In this project, a compiler mechanism is used which includes five main stages, namely Lexical Analysis (Lexer), Syntax Analysis (Parser), Semantic Analysis, Intermediate Code Generation, and Interpreter.</p>

<p align="justify">In the first stage, Lexical Analysis, the system is designed and implemented to scan Pascal-S source code and convert it into a sequence of tokens using Deterministic Finite Automata (DFA). This lexer identifies elements such as keywords, identifiers, operators, numbers, and symbols, forming the foundational step for the subsequent phases of compilation.</p>

<p align="justify">In the second stage, Syntax Analysis (Parser), the system processes the sequence of tokens produced by the lexer and constructs a Parse Tree based on the grammar rules of the adjusted Pascal-S. Using a recursive descent parsing approach, the parser validates whether the token stream conforms to the language specification and forms a hierarchical representation of the program structure.</p>

<p align="justify">In the third stage, Semantic Analysis, the compiler verifies the meaning and consistency of the parsed program by building and analyzing the AST and populating a symbol table. This phase ensures that identifiers are properly declared before use, validates type correctness across expressions and operations, and checks semantic rules such as scope resolution, procedure/function matching, and constant usage. Semantic errors are reported with clear diagnostics, allowing inconsistencies or invalid constructs to be detected early before intermediate code generation.</p>

---

## Requirement <a name="requirement"></a>

<div align="right">(<a href="#table-of-contents">back to top</a>)</div>

- **Programming Language:** Python 3.10 or newer

---

## Installation and Usage <a name="installation-and-usage"></a>

<div align="right">(<a href="#table-of-contents">back to top</a>)</div>

> [!WARNING]  
> Only Lexical Analyzer (Lexer) and Parser has been implemented (as of November 16, 2025).

1. **Clone or download the repository**

   ```bash
   git clone https://github.com/Kurondt/SMN-Tubes-IF2224.git
   cd SMN-Tubes-IF2224
   ```

2. **Run the program (lexical + syntax analyzer)**

   ```bash
   # python -m src.main <source .pas file> --dfa <path to dfa rules, optional, default to src/rules/dfa.json>
   # Example:

   python -m src.main test/milestone-3/program.pas
   ```

3. **Output**

   - Prints all identified tokens, parse tree, symbol tables, and decorated AST result.
   - If lexical, syntax, or semantic errors occur, the program will print informative error messages in the terminal

---

## Task Distribution <a name="task-distribution"></a>

<div align="right">(<a href="#table-of-contents">back to top</a>)</div>

| NIM      | Member Name               | Milestone 1                                         | Milestone 2                                    | Milestone 3                                | Milestone 4 | Milestone 5 |
| -------- | ------------------------- | --------------------------------------------------- | ---------------------------------------------- | ------------------------------------------ | ----------- | ----------- |
| 13523002 | Refki Alfarizi            | Project setup and basic functionality               | Project Setup and Report                       | Designed and implemented Semantic Analyzer |             |             |
| 13523028 | Muhammad Aditya Rahmadeni | Designed DFA rules and implemented rule loaders     | Adjust DFA Rule for Range operator             | Adjusted DFA rule                          |             |             |
| 13523088 | Aryo Bama Wiratama        | Designed and implemented scanner/lexer algorithm    | Designed and Implemented Grammar               | Designed and implemented AST nodes         |             |             |
| 13523116 | Fityatul Haq Rosyidi      | Designed and implemented character stream mechanism | Designed and Implemented ParseTree and Grammar | Adjusted Parser/Syntax Analyzer            |             |             |

---

<p></p>
<p align="center">

   <img width="500" height="250" alt="image" src="./assets/saymyname.gif" />

   <br>
   <em><strong></strong></em>
</p>
