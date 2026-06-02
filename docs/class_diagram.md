```mermaid
---
title: Domain Layer
---
classDiagram
    
    class Card{
        string name
        string canonical_name
        int oracle_id
        string set_name
        string set_code
        __get_canonical_card()
        __get_oracle_id()

    }

    class Vendor{
        string name
        string url
        Scrapper scrapper
        get_prices()
    }

    class Offer{
        Card card
        Vendor vendor
        float price
        bool in_stock
        int stock
        bool holo
        string version
        string condition
    }

    ```