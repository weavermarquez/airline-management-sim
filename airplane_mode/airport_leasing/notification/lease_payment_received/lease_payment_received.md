<h2 id="hello-docleased_to">Hello {{ doc.leased_to }},</h2>

<p>You have successfully submitted a payment for lease {{ doc.name }} for room {{ doc.leasing_of }}.
You now have an outstanding balance of {{ doc.outstanding_balance }}. 
It is currently {{ doc.status }}.</p>

<pre><code>Next invoice sent on: *{{ doc.next_date }}*
End of lease: *{{ doc.end_date }}*
</code></pre>

<p>Best Regards,</p>

<p>{{ doc.leased_from }} Management</p>
