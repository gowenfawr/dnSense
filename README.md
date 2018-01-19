# dnSense
Preventative treatment for DNS Cache Snooping on Internal DNS servers

(Current status: Works, but needs warm fuzzy stuff like command line
options and config file handling to be fleshed out)

# The Problem
DNS Cache Snooping occurs when a caching recursive name server is 
queried in order to determine what queries other systems on the 
network have been making.  If Alice's desktop has McAfee Anti-Virus
installed, and checks for updates regularly, then Bob will be able
to tell that McAfee is in use by querying Alice's DNS server and
seeing that an entry for McAfee's update server is already cached.

Note that this is *entirely as designed* and cannot be mitigated 
without discarding caching completely, which would negatively impact
the performance and reliability of network access.  Additionally, 
since your caching resolvers should be on your internal network, an 
attacker needs to have already gained access to your internal network
to perform this minor research.

# The Point of Pain
[Nessus](https://www.tenable.com/plugins/index.php?view=single&id=12217)
considers this minor, unavoidable information gathering method
to be a CVSS 5.0, which is high enough to require remediation under
PCI.  And they provide the helpful advice "Contact the vendor of the 
DNS software for a fix", which ignores the fact that there is no fix
by *any* software vendor which will address the issue **and** leave the
network in a functioning state.

# Prevention
The only way you can have a caching resolver for your internal systems
and avoid communicating the identity of your defensive tools is to 
pre-emptively populate the cache with indicators of tools which you 
aren't using.  That's where dnSense comes in.  It will take in a list
of DNS names that indicate use of known defensive software, and will 
query those names regularly enough to keep them in the cache.  An 
attacker might be able to see indications that you're running McAfee, 
and Symantec, and Kaspersky, and Sophos - but they won't know which 
of them you're *actually* running.

# Preposterous!
Yes.  It is.  In fact, the name "dnSense" is intentionally 
homophonous to "nonsense".  It reflects the author's opinion that 
treating DNS Cache Snooping as a defect to be avoided, when it is in 
fact an unalterable aspect of the DNS infrastructure we rely upon
without viable alternative, is nonsense.

But if we're getting dinged on our PCI compliance because of it, then 
heck, why not do something stupid but inoffensive about it?

# Practical impact?

Minimal.  Just have a host on your network running dnSense, and it'll 
continue to query a few dozen names regularly, based on the TTL of the
targets.

(This is usually on the order of every 60 seconds.  Note that the
published names usually resolve to a larger number of dynamic names with 
much smaller TTLs, like 1 second - dnSense doesn't refresh those by TTL,
only the name it was asked to keep in the cache.)

In the big scheme of DNS volume, with vendors who are willing to 
drop individual TTLs as low as 1 second, it'll be unnoticeable.
