
# Kaitlyn

![Kaitlyn](https://res.cloudinary.com/haks/image/upload/v1578852712/circle-cropped_1.png)

Kaitlyn is a Twitter bot that finds clones or possible duplicates of tweets.

## Usage

On the platform you can:

Tweet:

```
old @findclones
```

as a comment on a tweet to fetch clones of that tweet **before** it was created. These tweets are the possible originals.

Tweet:

```
new @findclones
```
as a comment on a tweet to fetch clones of that tweet **after** it was created. These tweets are possibly plagiarized.

Tweet:

```
go @findclones
```
as a comment on a tweet to fetch all clones of that tweet, regardless of when they were created.


## Local Deployment

To use on computer, ensure that you have Python 3 installed.

Assign proper values to the environment variables.

Run:

```
pip install -r requirements.txt
```

Run on terminal 

```
python worker.py
```

Run

```
python clock.py
```

## Running the tests

There are no tests yet.

## Contributing

Contributions are welcomed.


## Authors

* **Habeeb Kehinde Shopeju** - [HAKSOAT](https://github.com/HAKSOAT)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

Thanks to:
* [Deji Cranium](https://github.com/dejicranium)
* [Appcypher](https://github.com/appcypher)
* [Sanni Hussein](https://twitter.com/sannihussein)
* [Shalvah](https://github.com/shalvah)
* [Bakman](https://github.com/Tiemma)

and everyone who provided ideas to help make this project better.
