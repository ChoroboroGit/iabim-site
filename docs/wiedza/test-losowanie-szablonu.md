---
title: "Test losowania szablonu"
description: "Artykuł testowy do weryfikacji randomizacji szablonów generatora"
keywords: "test szablon generator"
author: "IABIM"
date: "2026-03-06"
layout: "C"
---

<!--
================================================================================
INSTRUKCJA EDYCJI ARTYKUŁU
================================================================================

HERO (główne zdjęcie):
- Wrzuć zdjęcie jako: docs/img/wiedza/SLUG/hero.jpg
- Wyświetli się automatycznie pod tytułem
- Pojawi się też w miniaturkach na liście artykułów
- Brak hero.jpg = brak zdjęcia głównego

ZDJĘCIA W TREŚCI:
- Placeholdery są na końcu pliku (przed "Powiązane artykuły")
- Wytnij, wklej gdzie chcesz, odkomentuj (usuń < ! - - i - - >)
- Zmień opis i numer pliku
- Wrzuć zdjęcia do: docs/img/wiedza/SLUG/
- Kompresja automatyczna przy renderze strony

DIAGRAMY (tylko szablony B i C):
- Edytuj tekst w bloku mermaid
- Zmień placeholdery: KROK 1, WYZWANIE, itd.
- Podgląd: https://mermaid.live

STRUKTURA:
- Wypełnij sekcje oznaczone [w nawiasach kwadratowych]
- Zachowaj hierarchię nagłówków (H2, H3)
- Usuń sekcje których nie potrzebujesz

STATUS W CSV:
- new = do wygenerowania
- draft = w edycji (niewidoczny na stronie)
- published = widoczny na stronie

DEPLOY:
python -m mkdocs gh-deploy --clean --force
================================================================================
-->

# Test losowania szablonu

{{ wiedza_hero("test-losowanie-szablonu") }}

Artykuł testowy do weryfikacji randomizacji szablonów generatora

---

## Co to jest?

[Wyjaśnij pojęcie lub zagadnienie]

!!! info "Definicja"
    [Krótka definicja terminu]

## Dlaczego to ważne?

[Uzasadnij znaczenie tematu]

### Korzyści

| Korzyść | Opis |
|---------|------|
| [Korzyść 1] | [Opis] |
| [Korzyść 2] | [Opis] |
| [Korzyść 3] | [Opis] |

## Jak to zrobić?

[Przedstaw instrukcję krok po kroku]

### Schemat działania

```mermaid
flowchart LR
    P[PRZYGOTOWANIE] --> W[WYKONANIE] --> S{SPRAWDZENIE}
    S -->|OK| K[KONIEC]
    S -->|BŁĄD| W
```

### Krok 1: [Nazwa]

[Opis kroku]

### Krok 2: [Nazwa]

[Opis kroku]

### Krok 3: [Nazwa]

[Opis kroku]

## Checklist

- [ ] [Zadanie 1]
- [ ] [Zadanie 2]
- [ ] [Zadanie 3]
- [ ] [Zadanie 4]
- [ ] [Zadanie 5]

!!! warning "Uwaga"
    [Najważniejsze ostrzeżenie lub wskazówka]


<!-- ZDJĘCIA - odkomentuj i użyj gdzie potrzebujesz w artykule -->
<!-- ![Opis zdjęcia](../img/wiedza/test-losowanie-szablonu/01.jpg) -->
<!-- ![Opis zdjęcia](../img/wiedza/test-losowanie-szablonu/02.jpg) -->
<!-- ![Opis zdjęcia](../img/wiedza/test-losowanie-szablonu/03.jpg) -->

---

{{ wiedza_powiazane("test-losowanie-szablonu") }}

<p style="text-align: center; margin-top: 2rem;">
  <a href="../" class="btn btn-outline">Powrót do centrum wiedzy</a>
</p>
