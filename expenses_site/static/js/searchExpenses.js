const searchField = document.querySelector('#searchField');


searchField.addEventListener('keyup', (e) => {
    const searchValue = e.target.value;
    
    if (searchValue.trim().length > 0) {
        fetch("/search-expenses", {
            body: JSON.stringify({ searchText: searchValue }),
            method: "POST",
            headers : { 
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        }).then((response) => response.json())
        .then((data) => {
            console.log(data);
        }).catch(error => {console.error(error);});
    }
})