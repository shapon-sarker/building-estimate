document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('calculatorForm');
    const results = document.getElementById('results');
    const materialTypeSelect = document.querySelector('select[name="material_type"]');
    const aggregateLabel = document.getElementById('aggregate_label');

    // Update RCC ratio total
    function updateRccRatioTotal() {
        const type1 = parseFloat(document.querySelector('input[name="rcc_ratio_type_1"]').value) || 0;
        const type2 = parseFloat(document.querySelector('input[name="rcc_ratio_type_2"]').value) || 0;
        const type3 = parseFloat(document.querySelector('input[name="rcc_ratio_type_3"]').value) || 0;
        document.getElementById('total_ratio').value = (type1 + type2 + type3).toFixed(2);
    }

    // Add event listeners to RCC ratio inputs
    document.querySelectorAll('input[name^="rcc_ratio_"]').forEach(input => {
        input.addEventListener('input', updateRccRatioTotal);
    });

    // Update material type label
    materialTypeSelect.addEventListener('change', function() {
        aggregateLabel.textContent = this.value === 'stone' ? 'Stone/Brick Chips (CFT)' : 'Brick Nos';
    });

    // Format number with commas and decimal places
    function formatNumber(number, decimals = 2) {
        return number.toLocaleString('en-US', {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        });
    }

    // Collect form data
    function collectFormData() {
        const formData = {
            rcc_ratio: {
                type_1: document.querySelector('input[name="rcc_ratio_type_1"]').value,
                type_2: document.querySelector('input[name="rcc_ratio_type_2"]').value,
                type_3: document.querySelector('input[name="rcc_ratio_type_3"]').value
            },
            rates_and_wastage: {
                wastage_percent: document.querySelector('input[name="wastage_percent"]').value,
                cement_rate: document.querySelector('input[name="cement_rate"]').value,
                sand_rate: document.querySelector('input[name="sand_rate"]').value,
                aggregate_rate: document.querySelector('input[name="aggregate_rate"]').value,
                brick_rate: document.querySelector('input[name="brick_rate"]').value,
                rebar_rate: document.querySelector('input[name="rebar_rate"]').value,
                formwork_rate: document.querySelector('input[name="formwork_rate"]').value,
                casting_rate: document.querySelector('input[name="casting_rate"]').value
            }
        };

        // Collect column data
        for (let i = 1; i <= 15; i++) {
            const typeKey = `type_${i}`;
            const columnNos = document.querySelector(`input[name="${typeKey}_column_nos"]`).value;
            
            if (columnNos) {
                formData[typeKey] = {
                    column_nos: columnNos,
                    length: document.querySelector(`input[name="${typeKey}_length"]`).value,
                    breadth: document.querySelector(`input[name="${typeKey}_breadth"]`).value,
                    clear_cover: document.querySelector(`input[name="${typeKey}_clear_cover"]`).value,
                    height: document.querySelector(`input[name="${typeKey}_height"]`).value,
                    large_dia_size: document.querySelector(`input[name="${typeKey}_large_dia_size"]`).value,
                    large_dia_nos: document.querySelector(`input[name="${typeKey}_large_dia_nos"]`).value,
                    small_dia_size: document.querySelector(`input[name="${typeKey}_small_dia_size"]`).value,
                    small_dia_nos: document.querySelector(`input[name="${typeKey}_small_dia_nos"]`).value,
                    development_length: document.querySelector(`input[name="${typeKey}_development_length"]`).value,
                    tie_rod_size: document.querySelector(`input[name="${typeKey}_tie_rod_size"]`).value,
                    tie_spacing: document.querySelector(`input[name="${typeKey}_tie_spacing"]`).value,
                    hook_length: document.querySelector(`input[name="${typeKey}_hook_length"]`).value,
                    extra_tie_1: document.querySelector(`input[name="${typeKey}_extra_tie_1"]`).value,
                    extra_tie_2: document.querySelector(`input[name="${typeKey}_extra_tie_2"]`).value
                };
            }
        }

        return formData;
    }

    // Update results in the UI
    function updateResults(data) {
        // Update material quantities and costs
        document.getElementById('cement_qty').textContent = formatNumber(data.results.cement);
        document.getElementById('sand_qty').textContent = formatNumber(data.results.sand);
        document.getElementById('aggregate_qty').textContent = formatNumber(data.results.aggregate);
        document.getElementById('rebar_qty').textContent = formatNumber(data.results.rebar); // Already in tons
        document.getElementById('formwork_qty').textContent = formatNumber(data.results.formwork);
        document.getElementById('casting_qty').textContent = formatNumber(data.results.casting);

        // Update wastage percentage
        document.getElementById('wastage_percent_display').textContent = 
            formatNumber(parseFloat(document.querySelector('input[name="wastage_percent"]').value));

        // Update total quantities with wastage
        document.getElementById('cement_total').textContent = formatNumber(data.results.cement);
        document.getElementById('sand_total').textContent = formatNumber(data.results.sand);
        document.getElementById('aggregate_total').textContent = formatNumber(data.results.aggregate);
        document.getElementById('rebar_total').textContent = formatNumber(data.results.rebar); // Already in tons
        document.getElementById('formwork_total').textContent = formatNumber(data.results.formwork);
        document.getElementById('casting_total').textContent = formatNumber(data.results.casting);

        // Update rates
        document.getElementById('cement_rate').textContent = formatNumber(data.rates.cement);
        document.getElementById('sand_rate').textContent = formatNumber(data.rates.sand);
        document.getElementById('aggregate_rate').textContent = formatNumber(data.rates.aggregate);
        document.getElementById('rebar_rate').textContent = formatNumber(data.rates.rebar); // Rate per ton
        document.getElementById('formwork_rate').textContent = formatNumber(data.rates.formwork);
        document.getElementById('casting_rate').textContent = formatNumber(data.rates.casting);

        // Update amounts
        document.getElementById('cement_amount').textContent = formatNumber(data.costs.cement);
        document.getElementById('sand_amount').textContent = formatNumber(data.costs.sand);
        document.getElementById('aggregate_amount').textContent = formatNumber(data.costs.aggregate);
        document.getElementById('rebar_amount').textContent = formatNumber(data.costs.rebar); // Cost based on tons
        document.getElementById('formwork_amount').textContent = formatNumber(data.costs.formwork);
        document.getElementById('casting_amount').textContent = formatNumber(data.costs.casting);

        // Update total amount
        const totalAmount = Object.values(data.costs).reduce((sum, cost) => sum + cost, 0);
        document.getElementById('total_amount').textContent = formatNumber(totalAmount);

        // Update rebar quantities by size (convert kg to tons)
        document.getElementById('rebar_8mm').textContent = formatNumber(data.rebar_sizes[8] / 1000);
        document.getElementById('rebar_10mm').textContent = formatNumber(data.rebar_sizes[10] / 1000);
        document.getElementById('rebar_12mm').textContent = formatNumber(data.rebar_sizes[12] / 1000);
        document.getElementById('rebar_16mm').textContent = formatNumber(data.rebar_sizes[16] / 1000);
        document.getElementById('rebar_20mm').textContent = formatNumber(data.rebar_sizes[20] / 1000);
        document.getElementById('rebar_25mm').textContent = formatNumber(data.rebar_sizes[25] / 1000);
        document.getElementById('rebar_28mm').textContent = formatNumber(data.rebar_sizes[28] / 1000);
        document.getElementById('rebar_32mm').textContent = formatNumber(data.rebar_sizes[32] / 1000);

        // Show results with animation
        results.style.display = 'block';
        setTimeout(() => results.classList.add('show'), 10);
    }

    // Handle form submission
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Add loading state
        form.classList.add('loading');
        const submitButton = form.querySelector('button[type="submit"]');
        const originalText = submitButton.textContent;
        submitButton.textContent = 'Calculating...';
        submitButton.disabled = true;

        // Collect and send form data
        const formData = collectFormData();
        
        fetch('/calculate-short-tied-column', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateResults(data);
            } else {
                alert('Error: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while calculating. Please try again.');
        })
        .finally(() => {
            // Remove loading state
            form.classList.remove('loading');
            submitButton.textContent = originalText;
            submitButton.disabled = false;
        });
    });

    // Handle form reset
    form.addEventListener('reset', function() {
        results.classList.remove('show');
        setTimeout(() => results.style.display = 'none', 300);
        updateRccRatioTotal();
    });

    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}); 