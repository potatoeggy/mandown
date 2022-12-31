The library supports a few more features that the CLI does not, including being able to work with raw `BaseComic` and `BaseMetadata` objects, querying sources directly, or perform operations on Mandown comics stored in the file system.

## Querying

If you want to do whatever you want with Mandown's sources, you can use the `mandown.query` function. This function returns a `BaseComic`, which contains two fields: `metadata` and `chapters`. The former is a `BaseMetadata` object, and the latter is a list of `BaseChapter` objects.

```python
import mandown

comic: BaseComic = mandown.query("https://example.com/comic")

print(comic.metadata.title, comic.chapters[0].title)
```
