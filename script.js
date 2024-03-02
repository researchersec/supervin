document.addEventListener('DOMContentLoaded', async function () {
    const searchInput = document.getElementById('searchInput');
    const wineTableBody = document.getElementById('wineTableBody');

    const response = await fetch('supervin.db');
    const buffer = await response.arrayBuffer();
    const SQL = await initSqlJs({ locateFile: () => 'https://cdnjs.cloudflare.com/ajax/libs/sql.js/1.5.0/sql-wasm.wasm' });
    const db = new SQL.Database(new Uint8Array(buffer));

    function loadWines() {
        const query = 'SELECT * FROM wines';
        const result = db.exec(query);
        renderTable(result[0].values);
    }

    function renderTable(data) {
        wineTableBody.innerHTML = '';
        data.forEach(wine => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${wine[1]}</td>
                <td>${wine[2]}</td>
                <td>${wine[3]}</td>
                <td>${wine[5]}</td>
                <td><img src="${wine[4]}" alt="${wine[1]}" style="width: 100px;"></td>
            `;
            wineTableBody.appendChild(row);
        });
    }

    loadWines();

    searchInput.addEventListener('input', function () {
        const searchValue = this.value.toLowerCase();
        const query = `SELECT * FROM wines WHERE name LIKE '%${searchValue}%' OR country LIKE '%${searchValue}%'`;
        const result = db.exec(query);
        renderTable(result[0].values);
    });
});
