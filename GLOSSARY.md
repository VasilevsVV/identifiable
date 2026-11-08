# identifiable

`identifiable` gives the objects of a family of classes IDs, keeps them in one registry per family,
and finds them by ID.

## Language

**ID**:
The name that identifies one object within its family. It's derived from the arguments the
object is created with, so it can be known before the object exists.
_Avoid_: key, unique ID (without saying unique within what)

**Family**:
A family base plus all of its subclasses, sharing one registry.
_Avoid_: hierarchy, group

**Family base**:
The base class that mixes in `Identifiable` directly and names the family.
_Avoid_: root, direct subclass

**Registry**:
All objects of one family, indexed by ID. There's one per family, so an ID is unique across the
whole family.
_Avoid_: class objects map, store

**Duplicate**:
An attempt to create an object whose ID is already in its family's registry.

**ID reference**:
Holding an object's ID instead of the object, and looking the object up when needed.
_Avoid_: pointer, soft pointer, soft reference
