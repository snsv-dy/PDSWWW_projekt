// move to static

var static_input_ids = [
	{ name: 'title', id: "test_title" },
	{ name: 'points', id: "test_points" },
	{ name: 'question', id: "test_question" }
]

function create_input(name, value) {
	var inp = document.createElement('input');
	inp.type = 'hidden';
	inp.name = name;
	inp.value = value;
	return inp;
}

function post_all_inputs(destination) {

	console.log('destination', destination);

	var form = document.createElement('form');
	form.method = 'post';
	form.action = destination;
	form.style.display = 'none';
	for (let param of static_input_ids) {
		var elem = document.getElementById(param.id);
		// var clone = document.createElement('input');
		// clone.type = 'hidden';
		// clone.name = param.name;
		// clone.value = elem.value;
		form.appendChild(create_input(param.name, elem.value));
	}

	// var index = document.createElement('input');
	// index.name = 'question_index';
	// index.type = 'hidden';
	// index.value = ;
	form.appendChild(create_input('question_index', document.forms[1].question_index.value));

	var question_type = document.forms[1].question_type.value;
	form.appendChild(create_input('question_type', question_type));

	if ('anwser_text' in document.forms[1] && (question_type == '0' || question_type == '1')) {
		if(typeof document.forms[1].anwser_text[Symbol.iterator] === 'function'){
			for (let e of document.forms[1].anwser_text) {
				form.appendChild(create_input(e.name, e.value));
			}
		}else{
			var e = document.forms[1].anwser_text;
			form.appendChild(create_input(e.name, e.value));
		}
	}

	document.body.appendChild(form);

	form.submit();
}

function add_anwser(type) {
	var div = document.createElement('div'); 
	div.className = 'input-group mb-3';

	var div_prepend = document.createElement('div');
	div_prepend.className = 'input-group-prepend';

	var div_text = document.createElement('div');
	div_text.className = 'input-group-text';

	var checkbox = document.createElement('input');
	checkbox.type = type == '0' ? 'checkbox' : 'radio';
	checkbox.name = 'anwser';
	div_text.appendChild(checkbox);

	div_prepend.appendChild(div_text);
	div.appendChild(div_prepend);

	var text = document.createElement('input');
	text.type = 'text';
	text.name = 'anwser_text';
	text.placeholder = 'Odpowiedź';
	text.className = 'form-control';
	div.appendChild(text);

	var remove = document.createElement('button');
	remove.textContent = 'X';
	remove.className = 'btn btn-danger';
	remove.addEventListener('click', function () {
		remove_anwser(remove);
	});

	div.appendChild(remove);

	document.forms[1].insertBefore(div, document.forms[1].lastElementChild);
}

function remove_anwser(e) {
	console.log(e);
	document.forms[1].removeChild(e.parentElement);
}