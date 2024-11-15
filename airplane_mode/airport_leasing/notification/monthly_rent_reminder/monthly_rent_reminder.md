<h2 id="hello-docleased_to">Hello {{ doc.leased_to }},</h2>

<p>This is your monthly reminder that lease {{ doc.name }} for room {{ doc.leasing_of }} has an outstanding balance of {{ doc.outstanding_balance }}. 
It is currently {{ doc.status }}.</p>

<pre><code>Next invoice sent on: *{{ doc.next_date }}*
End of lease: *{{ doc.end_date }}*
</code></pre>

<p>Best Regards,</p>

<p>{{ doc.leased_from }} Management</p>
