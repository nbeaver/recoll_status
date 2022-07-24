Dear ericmarceau-rogers,
Thanks for your interest in my script. I have just now [added a flag](https://github.com/nbeaver/recoll_status/commit/25b29b8f14c1e9f3c12b01c987cd149e4a0b2a7f) that allows overriding the location of `dbdir`. You can pass it whatever is the parent directory for `flintlock`, e.g. for `/XAPIANDB/flintlock` it would be this:

    recoll_status.py --dbdir '/XAPIANDB/'

I hope this will be sufficient. I have tried to avoid the complexity of parsing the `recoll.conf` file and did not foresee the need for handling more advanced setups such as yours. I did note that the `idxstatus` file might not be in the default location and so put parsing the `recoll.conf` file to check on the [to-do list](https://github.com/nbeaver/recoll_status/blob/25b29b8f14c1e9f3c12b01c987cd149e4a0b2a7f/todo.md), but alas I have not had time to implement this.
