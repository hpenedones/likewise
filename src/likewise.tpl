% rebase('base.tpl', title='Likewise')
% for image in images:
	<div class="nearimage">
	<div class="crop">
	<a href="/nearest/{{pagination[1]}}/{{image['key']}}">
		<img class="centered" src="/images/{{image['key']}}" />
	</a>
	</div>
	<p>Image: {{image['key']}}</p>
	<p>Distance: {{image['distance']}}</p>
	</div>
% end
