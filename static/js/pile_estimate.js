document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('pileEstimateForm');
    const results = document.getElementById('results');
    const resultsTable = document.getElementById('resultsTable');
    const printButton = document.getElementById('printButton');

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Collect form data
        const formData = {};
        
        // Collect pile data (A-F)
        ['A', 'B', 'C', 'D', 'E', 'F'].forEach(letter => {
            formData[letter] = [];
            for (let i = 1; i <= 5; i++) {
                const value = form[`${letter}${i}`].value;
                formData[letter].push(value ? parseFloat(value) : null);
            }
        });

        // Collect ratio data
        formData.aa = parseFloat(form.aa.value) || 0;
        formData.bb = parseFloat(form.bb.value) || 0;
        formData.cc = parseFloat(form.cc.value) || 0;

        // Collect rebar data (G-O)
        ['G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O'].forEach(letter => {
            formData[letter] = [];
            for (let i = 1; i <= 5; i++) {
                const value = form[`${letter}${i}`].value;
                formData[letter].push(value ? parseFloat(value) : null);
            }
        });

        // Collect material rates and wastage
        formData.cement_rate = parseFloat(form.cement_rate.value) || 0;
        formData.sand_rate = parseFloat(form.sand_rate.value) || 0;
        formData.stone_rate = parseFloat(form.stone_rate.value) || 0;
        formData.rebar_rate = parseFloat(form.rebar_rate.value) || 0;
        
        // Add wastage percentages
        formData.cement_wastage = parseFloat(form.cement_wastage.value) || 0;
        formData.sand_wastage = parseFloat(form.sand_wastage.value) || 0;
        formData.stone_wastage = parseFloat(form.stone_wastage.value) || 0;
        formData.rebar_wastage = parseFloat(form.rebar_wastage.value) || 0;

        // Send data to server
        fetch('/calculate-pile', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        })
        .then(response => response.json())
        .then(data => {
            displayResults(data);
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while calculating. Please try again.');
        });
    });

    function displayResults(data) {
        // Clear previous results
        resultsTable.innerHTML = '';

        // Format number function
        const formatNumber = (num) => {
            return Number(num).toLocaleString('en-IN', {
                maximumFractionDigits: 2,
                minimumFractionDigits: 2
            });
        };

        // Add each result row
        const resultRows = [
            ['Cement', data.cement_bags, 'Bags', data.cement_cost],
            ['Sand', data.sand_cft, 'CFT', data.sand_cost],
            ['Stone Chips', data.stone_chips_cft, 'CFT', data.stone_cost],
            ['Rebar', data.rebar_ton, 'Ton', data.rebar_cost],
            ['Total RCC Casting', data.total_rcc_casting, 'CFT', '-']
        ];

        // Create table header
        const headerRow = document.createElement('tr');
        headerRow.innerHTML = `
            <th style="width: 25%">Material</th>
            <th style="width: 25%">Quantity</th>
            <th style="width: 20%">Unit</th>
            <th style="width: 30%" class="text-end">Amount (TK)</th>
        `;
        resultsTable.appendChild(headerRow);

        // Add material rows
        resultRows.forEach(([label, quantity, unit, cost]) => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td class="fw-bold">${label}</td>
                <td class="text-end">${typeof quantity === 'string' ? quantity : Number(quantity).toFixed(2)}</td>
                <td>${unit}</td>
                <td class="text-end">${cost === '-' ? '-' : formatNumber(cost)} ${cost === '-' ? '' : 'TK'}</td>
            `;
            resultsTable.appendChild(row);
        });

        // Add total amount row
        const totalRow = document.createElement('tr');
        totalRow.classList.add('table-primary', 'fw-bold');
        totalRow.innerHTML = `
            <td colspan="3" class="text-end pe-4">Total Amount</td>
            <td class="text-end">${formatNumber(data.total_amount)} TK</td>
        `;
        resultsTable.appendChild(totalRow);

        // Show results section
        results.classList.remove('d-none');
    }

    printButton.addEventListener('click', function() {
        window.print();
    });
});
