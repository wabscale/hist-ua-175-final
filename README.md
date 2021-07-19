# Hist 175 Final Project

```graphql
{
    root(func: type(Root)) {
        countries(first: 10) {
            country

            people(first: 30) {
                name
                naid

                age : ~people {
                    age
                }

                age_of_entry : ~people {
                    age_of_entry
                }

                age_of_naturalization : ~people {
                    age_of_naturalization
                }

                port_of_entry : ~people {
                    port_of_entry
                }
            }
        }
    }
}
```

![alt img/img2.png](img/img2.png)


---

```graphql
{
    root(func: type(Root)) {
        countries(first: 10) {
            country

            people(first: 30) {
                name
                naid
            }
        }

        ports_of_entry(first: 10) {
            port_of_entry

            people(first: 30) {
                name
                naid
            }
        }
    }
}
```

![alt img/img1.png](img/img1.png)
