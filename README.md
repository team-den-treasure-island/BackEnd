# BackEnd

## Endpoints:

### Resource: Player

```javascript
// GET to /player/:id
// response:
{
  "id": 1,
  "name": "Kobe",
  "current_room": 0,
  "cooldown": "0.00",
  "explore_mode": false,
  "encumbrance": 0,
  "speed": 0,
  "gold": 0,
  "created_at": "2019-07-30T03:06:25.046927Z",
  "updated_at": "2019-07-30T03:11:37.036643Z"
}

// POST to /player/
// post object only required field is name, the rest are optional. Must have / at end of request
{
    "name":"Lou"
}
// response:
{
  "id": 4,
  "name": "Lou",
  "current_room": 0,
  "cooldown": "0.00",
  "explore_mode": false,
  "encumbrance": 0,
  "speed": 0,
  "gold": 0,
  "created_at": "2019-07-30T03:25:55.393732Z",
  "updated_at": "2019-07-30T03:25:55.393762Z"
}

// PUT to /player/:id/
// all fields (except created_at/updated_at) required to edit. If only looking to edit select fields, use a PATCH request to /player/:id/

// DELETE to /plauer/:id

```

### Resource: Room

```javascript
// GET to /room/:room_id
// response:
{
  "room_id": 1,
  "coord_x": 1,
  "coord_y": 1,
  "elevation": 1,
  "terrain": "rough terrain",
  "n_to": 0,
  "s_to": 0,
  "e_to": 0,
  "w_to": 0,
  "created_at": "2019-07-29T22:34:16.317891Z",
  "updated_at": "2019-07-29T22:34:16.317923Z"
}

// Post to /room/
// required fields room_id, coord_x, coord_y, elevation

// PUT to /room/:room_id/

// Patch to /room/:room_id/

// Delete to /room/:room_id

```
