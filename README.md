# Hist 127 

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
