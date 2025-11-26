document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('healthForm');
    const resultSection = document.getElementById('resultSection');
    const foodInput = document.getElementById('foodInput');
    const suggestionsBox = document.getElementById('suggestions');
    const selectedFoodsContainer = document.getElementById('selectedFoods');
    const hiddenFoodText = document.getElementById('foodText');

    let riskChart = null;
    let selectedFoods = [];
    let foodList = []; // Will fetch from server

    // 1. Fetch Food List on Load
    fetch('/api/foods')
        .then(res => res.json())
        .then(data => {
            foodList = data;
            console.log("Loaded foods:", foodList.length);
        })
        .catch(err => console.error("Error loading foods:", err));

    // 2. Autocomplete Logic
    foodInput.addEventListener('input', function () {
        const query = this.value.toLowerCase();
        suggestionsBox.innerHTML = '';

        if (query.length < 2) {
            suggestionsBox.style.display = 'none';
            return;
        }

        const matches = foodList.filter(f => f.toLowerCase().includes(query)).slice(0, 10);

        if (matches.length > 0) {
            matches.forEach(food => {
                const div = document.createElement('div');
                div.className = 'suggestion-item';
                div.innerText = food;
                div.onclick = () => addFood(food);
                suggestionsBox.appendChild(div);
            });
            suggestionsBox.style.display = 'block';
        } else {
            suggestionsBox.style.display = 'none';
        }
    });

    // Hide suggestions when clicking outside
    document.addEventListener('click', function (e) {
        if (e.target !== foodInput && e.target !== suggestionsBox) {
            suggestionsBox.style.display = 'none';
        }
    });

    function addFood(name) {
        if (!selectedFoods.includes(name)) {
            selectedFoods.push(name);
            renderTags();
            updateHiddenInput();
        }
        foodInput.value = '';
        suggestionsBox.style.display = 'none';
    }

    function removeFood(name) {
        selectedFoods = selectedFoods.filter(f => f !== name);
        renderTags();
        updateHiddenInput();
    }

    function renderTags() {
        selectedFoodsContainer.innerHTML = '';
        selectedFoods.forEach(food => {
            const tag = document.createElement('div');
            tag.className = 'food-tag';
            tag.innerHTML = `${food} <i class="fa-solid fa-xmark" onclick="removeFood('${food}')"></i>`;
            // Note: onclick inside innerHTML needs global scope function or event listener. 
            // Better to add event listener manually to avoid scope issues.
            tag.querySelector('i').addEventListener('click', () => removeFood(food));
            selectedFoodsContainer.appendChild(tag);
        });
    }

    function updateHiddenInput() {
        hiddenFoodText.value = selectedFoods.join(', ');
    }

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        if (selectedFoods.length === 0) {
            alert("Vui lòng chọn ít nhất một món ăn từ danh sách gợi ý!");
            return;
        }

        // Collect Data
        const userInfo = {
            age: document.getElementById('age').value,
            gender: document.getElementById('gender').value,
            height: document.getElementById('height').value,
            weight: document.getElementById('weight').value,
            smoking: document.getElementById('smoking').value
        };
        const foodText = hiddenFoodText.value;

        // Button Loading State
        const btn = form.querySelector('.btn-analyze');
        const originalBtnText = btn.innerHTML;
        btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Đang phân tích...';
        btn.disabled = true;

        try {
            const response = await fetch('/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ userInfo, foodText })
            });
            const data = await response.json();

            if (data.success) {
                showResults(data);
            } else {
                alert('Có lỗi xảy ra: ' + data.error);
            }

        } catch (error) {
            console.error(error);
            alert('Lỗi kết nối server!');
        } finally {
            btn.innerHTML = originalBtnText;
            btn.disabled = false;
        }
    });

    function showResults(data) {
        // 1. Show Section & Expand Layout
        document.querySelector('.dashboard').classList.add('has-results');
        resultSection.style.display = 'block';

        // Wait for transition slightly before scrolling
        setTimeout(() => {
            resultSection.scrollIntoView({ behavior: 'smooth' });
        }, 300);

        // 2. Update BMI
        const bmi = data.bmi;
        const bmiEl = document.getElementById('bmiDisplay');
        bmiEl.innerText = `BMI: ${bmi}`;
        if (bmi < 18.5) bmiEl.style.color = '#34D399'; // Underweight
        else if (bmi < 25) bmiEl.style.color = '#34D399'; // Normal
        else if (bmi < 30) bmiEl.style.color = '#FBBF24'; // Overweight
        else bmiEl.style.color = '#EF4444'; // Obese

        // 3. Update Nutrition (Animate numbers)
        animateValue("valCalo", 0, data.nutrition.calo, 1000);
        animateValue("valSugar", 0, data.nutrition.sugar, 1000);
        animateValue("valProtein", 0, data.nutrition.protein, 1000);

        // 4. Render Chart
        renderChart(data.predictions);

        // 5. Generate AI Insight
        generateInsight(data);
    }

    function animateValue(id, start, end, duration) {
        const obj = document.getElementById(id);
        let startTimestamp = null;
        const step = (timestamp) => {
            if (!startTimestamp) startTimestamp = timestamp;
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
            obj.innerHTML = Math.floor(progress * (end - start) + start);
            if (progress < 1) {
                window.requestAnimationFrame(step);
            }
        };
        window.requestAnimationFrame(step);
    }

    function renderChart(predictions) {
        const ctx = document.getElementById('riskChart').getContext('2d');

        if (riskChart) {
            riskChart.destroy();
        }

        riskChart = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: ['Tiểu đường', 'Tim mạch', 'Huyết áp cao'],
                datasets: [{
                    label: 'Nguy cơ (%)',
                    data: [predictions.diabetes, predictions.cardio, predictions.hypertension],
                    backgroundColor: 'rgba(236, 72, 153, 0.2)',
                    borderColor: '#EC4899',
                    pointBackgroundColor: '#fff',
                    pointBorderColor: '#EC4899',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: '#EC4899'
                }]
            },
            options: {
                scales: {
                    r: {
                        angleLines: { color: 'rgba(255, 255, 255, 0.1)' },
                        grid: { color: 'rgba(255, 255, 255, 0.1)' },
                        pointLabels: { color: '#F8FAFC', font: { size: 14 } },
                        ticks: { display: false, max: 100, min: 0 }
                    }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });
    }

    function generateInsight(data) {
        const el = document.getElementById('aiInsight');
        const foods = data.foods.join(', ');
        const risks = data.predictions;
        let msg = `<strong><i class="fa-solid fa-robot"></i> AI Nhận xét:</strong><br>`;

        msg += `Bạn đã ăn: ${foods || "Chưa xác định món"}.<br>`;
        msg += `Tổng nạp: ${Math.round(data.nutrition.calo)} kcal và ${Math.round(data.nutrition.sugar)}g đường.<br>`;

        if (risks.diabetes > 50) {
            msg += `<span style="color: #EF4444;">⚠️ Cảnh báo: Nguy cơ tiểu đường cao! Hãy giảm lượng đường ngay.</span><br>`;
        } else {
            msg += `<span style="color: #34D399;">✅ Nguy cơ tiểu đường ở mức an toàn.</span><br>`;
        }

        if (data.bmi > 25) {
            msg += `BMI của bạn hơi cao (${data.bmi}), hãy tập thể dục thêm nhé!`;
        }

        el.innerHTML = msg;
    }
});
