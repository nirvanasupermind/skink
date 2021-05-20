# Dictionary Types

Convenient type definitions for commonly used dictionary/map style objects
in TypeScript.


# Installation and usage

```bash
npm install --save dictionary-types
```

```typescript
import {
    Dictionary,
    ReadonlyDictionary,
    NumberMap,
    ReadonlyNumberMap
} from "dictionary-types";
```


## Dictionary\<T>

An object containing elements of type T, keyed by strings.

```typescript
const scores: Dictionary<number> = {
    "Amelia": 4,
    "Riley": 7,
    "April": 5
};

scores["Xander"] = 3;
```


## ReadonlyDictionary\<T>

A read-only object containing elements of type T, keyed by strings.

```typescript
function winner(scores: ReadonlyDictionary<number>): string {
    let winner = "";
    let highScore = 0;

    for (const name of Object.keys(scores)) {
        if (scores[name] > highScore) {
            highScore = scores[name];
            winner = name;
        }
    }

    return name;
}
```


## NumberMap\<T>

An object containing elements of type T, keyed by numbers.


## ReadonlyNumberMap\<T>

A read-only object containing elements of type T, keyed by numbers.


## Copyright

See [LICENSE.md](LICENSE.md).
