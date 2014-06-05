import click


@click.group()
def clicon():
	pass

@clicon.command()
def train():
	print "Training..."

@clicon.command()
def predict():
	print "Predicting..."


if __name__ == '__main__':
	clicon()