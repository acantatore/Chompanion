

<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
  <title>
  jsu152 / loadAnim / source &mdash; Bitbucket
</title>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
  <meta name="description" content="" />
  <meta name="keywords" content="" />
  <!--[if lt IE 9]>
  <script src="https://dwz7u9t8u8usb.cloudfront.net/m/22e5034559c2/js/lib/html5.js"></script>
  <![endif]-->

  <script>
    (function (window) {
      // prevent stray occurrences of `console.log` from causing errors in IE
      var console = window.console || (window.console = {});
      console.log || (console.log = function () {});

      var BB = window.BB || (window.BB = {});
      BB.debug = false;
      BB.cname = false;
      BB.CANON_URL = 'https://bitbucket.org';
      BB.MEDIA_URL = 'https://dwz7u9t8u8usb.cloudfront.net/m/22e5034559c2/';
      BB.images = {
        noAvatar: 'https://dwz7u9t8u8usb.cloudfront.net/m/22e5034559c2/img/no_avatar.png'
      };
      BB.user = {"isKbdShortcutsEnabled": true, "isSshEnabled": false};
      BB.user.has = (function () {
        var betaFeatures = [];
        betaFeatures.push('repo2');
        return function (feature) {
          return _.contains(betaFeatures, feature);
        };
      }());
      BB.targetUser = BB.user;
  
      BB.repo || (BB.repo = {});
  
      BB.user.isAdmin = false;
      BB.repo.id = 33513;
    
    
      BB.repo.language = null;
      BB.repo.pygmentsLanguage = null;
    
    
      BB.repo.slug = 'loadanim';
    
    
      BB.repo.owner = {
        username: 'jsu152'
      };
    
      // Coerce `BB.repo` to a string to get
      // "davidchambers/mango" or whatever.
      BB.repo.toString = function () {
        return BB.cname ? this.slug : this.owner.username + '/' + this.slug;
      }
    
    
      BB.changeset = 'b9aced46dcb6'
    
    
  
    }(this));
  </script>

  


  <link rel="stylesheet" href="https://dwz7u9t8u8usb.cloudfront.net/m/22e5034559c2/bun/css/bundle.css"/>



  <link rel="search" type="application/opensearchdescription+xml" href="/opensearch.xml" title="Bitbucket" />
  <link rel="icon" href="https://dwz7u9t8u8usb.cloudfront.net/m/22e5034559c2/img/logo_new.png" type="image/png" />
  <link type="text/plain" rel="author" href="/humans.txt" />


  
    <script src="https://dwz7u9t8u8usb.cloudfront.net/m/22e5034559c2/bun/js/bundle.js"></script>
  



</head>

<body id="" class="">
  <script>
    if (navigator.userAgent.indexOf(' AppleWebKit/') === -1) {
      $('body').addClass('non-webkit')
    }
    $('body')
      .addClass($.client.os.toLowerCase())
      .addClass($.client.browser.toLowerCase())
  </script>
  <!--[if IE 8]>
  <script>jQuery(document.body).addClass('ie8')</script>
  <![endif]-->
  <!--[if IE 9]>
  <script>jQuery(document.body).addClass('ie9')</script>
  <![endif]-->

  <div id="wrapper">



  <div id="header-wrap">
    <div id="header">
    <ul id="global-nav">
      <li><a class="home" href="http://www.atlassian.com">Atlassian Home</a></li>
      <li><a class="docs" href="http://confluence.atlassian.com/display/BITBUCKET">Documentation</a></li>
      <li><a class="support" href="/support">Support</a></li>
      <li><a class="blog" href="http://blog.bitbucket.org">Blog</a></li>
      <li><a class="forums" href="http://groups.google.com/group/bitbucket-users">Forums</a></li>
    </ul>
    <a href="/" id="logo">Bitbucket by Atlassian</a>

    <div id="main-nav">
    
      <ul class="clearfix">
        <li><a href="/plans">Pricing &amp; signup</a></li>
        <li><a id="explore-link" href="/explore">Explore Bitbucket</a></li>
        <li><a href="/account/signin/?next=/jsu152/loadanim/src/b9aced46dcb6/jquery.loadanim.js">Log in</a></li>
        

<li class="search-box">
  
    <form action="/repo/all">
      <input type="search" results="5" autosave="bitbucket-explore-search"
             name="name" id="searchbox"
             placeholder="owner/repo" />
  
  </form>
</li>

      </ul>
    
    </div>

  

    </div>
  </div>

    <div id="header-messages">
  
  
    
    
    
    
  

    
   </div>



    <div id="content">
      <div id="source">
      
  
  





  <script>
    jQuery(function ($) {
        var cookie = $.cookie,
            cookieOptions, date,
            $content = $('#content'),
            $pane = $('#what-is-bitbucket'),
            $hide = $pane.find('[href="#hide"]').css('display', 'block').hide();

        date = new Date();
        date.setTime(date.getTime() + 365 * 24 * 60 * 60 * 1000);
        cookieOptions = { path: '/', expires: date };

        if (cookie('toggle_status') == 'hide') $content.addClass('repo-desc-hidden');

        $('#toggle-repo-content').click(function (event) {
            event.preventDefault();
            $content.toggleClass('repo-desc-hidden');
            cookie('toggle_status', cookie('toggle_status') == 'show' ? 'hide' : 'show', cookieOptions);
        });

        if (!cookie('hide_intro_message')) $pane.show();

        $hide.click(function (event) {
            event.preventDefault();
            cookie('hide_intro_message', true, cookieOptions);
            $pane.slideUp('slow');
        });

        $pane.hover(
            function () { $hide.fadeIn('fast'); },
            function () { $hide.fadeOut('fast'); });

      (function () {
        // Update "recently-viewed-repos" cookie for
        // the "repositories" drop-down.
        var
          id = BB.repo.id,
          cookieName = 'recently-viewed-repos_' + BB.user.id,
          rvr = cookie(cookieName),
          ids = rvr? rvr.split(','): [],
          idx = _.indexOf(ids, '' + id);

        // Remove `id` from `ids` if present.
        if (~idx) ids.splice(idx, 1);

        cookie(
          cookieName,
          // Insert `id` as the first item, then call
          // `join` on the resulting array to produce
          // something like "114694,27542,89002,84570".
          [id].concat(ids.slice(0, 4)).join(),
          {path: '/', expires: 1e6} // "never" expires
        );
      }());
    });
  </script>



    <div id="what-is-bitbucket" class="new-to-bitbucket">
      <h2>Bruce Lueckenhoff <span id="slogan">is sharing code with you</span></h2>
      <img src="https://bitbucket-assetroot.s3.amazonaws.com/c/photos/2009/Dec/03/bruce-100x100_avatar.jpg" alt="" class="avatar" />
      <p>Bitbucket is a code hosting site. Unlimited public and private repositories. Free for small teams.</p>
      <div class="primary-action-link signup"><a href="/account/signup/?utm_source=internal&utm_medium=banner&utm_campaign=what_is_bitbucket">Try Bitbucket free</a></div>
      <a href="#hide" title="Don't show this again">Don't show this again</a>
    </div>


<div id="tabs" class="tabs">
  <ul>
    
      <li>
        <a href="/jsu152/loadanim/overview" id="repo-overview-link">Overview</a>
      </li>
    

    
      <li>
        <a href="/jsu152/loadanim/downloads" id="repo-downloads-link">Downloads (<span id="downloads-count">0</span>)</a>
      </li>
    

    
      
    

    
      <li>
        <a href="/jsu152/loadanim/pull-requests" id="repo-pr-link">Pull requests (0)</a>
      </li>
    

    
      <li class="selected">
        
          <a href="/jsu152/loadanim/src" id="repo-source-link">Source</a>
        
      </li>
    

    
      <li>
        <a href="/jsu152/loadanim/changesets" id="repo-commits-link">Commits</a>
      </li>
    

    
      <li id="wiki-tab" class="dropdown"
        style="display:
            block 
          
        ">
        <a href="/jsu152/loadanim/wiki" id="repo-wiki-link">Wiki</a>
      </li>
    

    
      <li id="issues-tab" class="dropdown inertial-hover"
        style="display:
          block 
          
        ">
        <a href="/jsu152/loadanim/issues?status=new&amp;status=open" id="repo-issues-link">Issues (0) &raquo;</a>
        <ul>
          <li><a href="/jsu152/loadanim/issues/new">Create new issue</a></li>
          <li><a href="/jsu152/loadanim/issues?status=new">New issues</a></li>
          <li><a href="/jsu152/loadanim/issues?status=new&amp;status=open">Open issues</a></li>
          <li><a href="/jsu152/loadanim/issues?status=duplicate&amp;status=invalid&amp;status=resolved&amp; status=wontfix">Closed issues</a></li>
          
          <li><a href="/jsu152/loadanim/issues">All issues</a></li>
          <li><a href="/jsu152/loadanim/issues/query">Advanced query</a></li>
        </ul>
      </li>
    

    
  </ul>

  <ul>
    
      <li>
        <a href="/jsu152/loadanim/descendants" id="repo-forks-link">Forks/queues (0)</a>
      </li>
    

    
      <li>
        <a href="/jsu152/loadanim/zealots">Followers (<span id="followers-count">1</span>)</a>
      </li>
    
  </ul>
</div>



 

  <div class="repo-menu" id="repo-menu">
    <ul id="repo-menu-links">
    
      <li>
        <a href="/jsu152/loadanim/rss" class="rss" title="RSS feed for loadAnim">RSS</a>
      </li>

      <li><a id="repo-fork-link" href="/jsu152/loadanim/fork" class="fork">fork</a></li>
      
        
          <li><a id="repo-patch-queue-link" href="/jsu152/loadanim/hack" class="patch-queue">patch queue</a></li>
        
      
      <li>
        <a id="repo-follow-link" rel="nofollow" href="/jsu152/loadanim/follow" class="follow">follow</a>
      </li>
      
          
      
      
        <li class="get-source inertial-hover">
          <a class="source">get source</a>
          <ul class="downloads">
            
              
              <li><a rel="nofollow" href="/jsu152/loadanim/get/b9aced46dcb6.zip">zip</a></li>
              <li><a rel="nofollow" href="/jsu152/loadanim/get/b9aced46dcb6.tar.gz">gz</a></li>
              <li><a rel="nofollow" href="/jsu152/loadanim/get/b9aced46dcb6.tar.bz2">bz2</a></li>
            
          </ul>
        </li>
      
    </ul>

  
    <ul class="metadata">
      
      
        <li class="branches inertial-hover">branches
          <ul>
            <li><a href="/jsu152/loadanim/src/b9aced46dcb6" title="default">default</a>
              
              
            </li>
          </ul>
        </li>
      
      
      <li class="tags inertial-hover">tags
        <ul>
          <li><a href="/jsu152/loadanim/src/b9aced46dcb6">tip</a>
            
            </li>
        </ul>
      </li>
     
     
    </ul>
  
</div>

<div class="repo-menu" id="repo-desc">
    <ul id="repo-menu-links-mini">
      

      
      <li>
        <a href="/jsu152/loadanim/rss" class="rss" title="RSS feed for loadAnim"></a>
      </li>

      <li><a href="/jsu152/loadanim/fork" class="fork" title="Fork"></a></li>
      
        
          <li><a href="/jsu152/loadanim/hack" class="patch-queue" title="Patch queue"></a></li>
        
      
      <li>
        <a rel="nofollow" href="/jsu152/loadanim/follow" class="follow">follow</a>
      </li>
      
          
      
      
        <li>
          <a class="source" title="Get source"></a>
          <ul class="downloads">
            
              
              <li><a rel="nofollow" href="/jsu152/loadanim/get/b9aced46dcb6.zip">zip</a></li>
              <li><a rel="nofollow" href="/jsu152/loadanim/get/b9aced46dcb6.tar.gz">gz</a></li>
              <li><a rel="nofollow" href="/jsu152/loadanim/get/b9aced46dcb6.tar.bz2">bz2</a></li>
            
          </ul>
        </li>
      
    </ul>

    <h3 id="repo-heading" class="public hg">
      <a class="owner-username" href="/jsu152">jsu152</a> /
      <a class="repo-name" href="/jsu152/loadanim">loadAnim</a>
    

    
    </h3>

    
      <p class="repo-desc-description">A JQuery plugin to provide a Yahoo-style animated &quot;Loading...&quot; tab.</p>
    

  <div id="repo-desc-cloneinfo">Clone this repository (size: 23.9 KB):
    <a href="https://bitbucket.org/jsu152/loadanim" class="https">HTTPS</a> /
    <a href="ssh://hg@bitbucket.org/jsu152/loadanim" class="ssh">SSH</a>
    <pre id="clone-url-https">hg clone https://bitbucket.org/jsu152/loadanim</pre>
    <pre id="clone-url-ssh">hg clone ssh://hg@bitbucket.org/jsu152/loadanim</pre>
    
  </div>

        <a href="#" id="toggle-repo-content"></a>

        

</div>




      
  <div id="source-container">
    

  <div id="source-path">
    <h1>
      <a href="/jsu152/loadanim/src" class="src-pjax">loadAnim</a> /

  
    
      <span>jquery.loadanim.js</span>
    
  

    </h1>
  </div>

  <div class="labels labels-csv">
  
    <dl>
  
    
  
  
    
  
  
    <dt>Branch</dt>
    
      
        <dd class="branch unabridged"><a href="/jsu152/loadanim/changesets/tip/branch(%22default%22)" title="default">default</a></dd>
      
    
  
</dl>

  
  </div>


  
  <div id="source-view">
    <div class="header">
      <ul class="metadata">
        <li><code>b9aced46dcb6</code></li>
        
          
            <li>60 loc</li>
          
        
        <li>1.6 KB</li>
      </ul>
      <ul class="source-view-links">
        
        <li><a id="embed-link" href="https://bitbucket.org/jsu152/loadanim/src/b9aced46dcb6/jquery.loadanim.js?embed=t">embed</a></li>
        
        <li><a href="/jsu152/loadanim/history/jquery.loadanim.js">history</a></li>
        
        <li><a href="/jsu152/loadanim/annotate/b9aced46dcb6/jquery.loadanim.js">annotate</a></li>
        
        <li><a href="/jsu152/loadanim/raw/b9aced46dcb6/jquery.loadanim.js">raw</a></li>
        <li>
          <form action="/jsu152/loadanim/diff/jquery.loadanim.js" class="source-view-form">
          
            <input type="hidden" name="diff2" value="b9aced46dcb6" />
            <select name="diff1">
            
              
            
              
                <option value="2fb6e1bac9a6">2fb6e1bac9a6</option>
              
            
              
                <option value="86e49d365ab8">86e49d365ab8</option>
              
            
              
                <option value="d477abbd6a57">d477abbd6a57</option>
              
            
            </select>
            <input type="submit" value="diff" />
          
          </form>
        </li>
      </ul>
    </div>
  
    <div>
    <table class="highlighttable"><tr><td class="linenos"><div class="linenodiv"><pre><a href="#cl-1"> 1</a>
<a href="#cl-2"> 2</a>
<a href="#cl-3"> 3</a>
<a href="#cl-4"> 4</a>
<a href="#cl-5"> 5</a>
<a href="#cl-6"> 6</a>
<a href="#cl-7"> 7</a>
<a href="#cl-8"> 8</a>
<a href="#cl-9"> 9</a>
<a href="#cl-10">10</a>
<a href="#cl-11">11</a>
<a href="#cl-12">12</a>
<a href="#cl-13">13</a>
<a href="#cl-14">14</a>
<a href="#cl-15">15</a>
<a href="#cl-16">16</a>
<a href="#cl-17">17</a>
<a href="#cl-18">18</a>
<a href="#cl-19">19</a>
<a href="#cl-20">20</a>
<a href="#cl-21">21</a>
<a href="#cl-22">22</a>
<a href="#cl-23">23</a>
<a href="#cl-24">24</a>
<a href="#cl-25">25</a>
<a href="#cl-26">26</a>
<a href="#cl-27">27</a>
<a href="#cl-28">28</a>
<a href="#cl-29">29</a>
<a href="#cl-30">30</a>
<a href="#cl-31">31</a>
<a href="#cl-32">32</a>
<a href="#cl-33">33</a>
<a href="#cl-34">34</a>
<a href="#cl-35">35</a>
<a href="#cl-36">36</a>
<a href="#cl-37">37</a>
<a href="#cl-38">38</a>
<a href="#cl-39">39</a>
<a href="#cl-40">40</a>
<a href="#cl-41">41</a>
<a href="#cl-42">42</a>
<a href="#cl-43">43</a>
<a href="#cl-44">44</a>
<a href="#cl-45">45</a>
<a href="#cl-46">46</a>
<a href="#cl-47">47</a>
<a href="#cl-48">48</a>
<a href="#cl-49">49</a>
<a href="#cl-50">50</a>
<a href="#cl-51">51</a>
<a href="#cl-52">52</a>
<a href="#cl-53">53</a>
<a href="#cl-54">54</a>
<a href="#cl-55">55</a>
<a href="#cl-56">56</a>
<a href="#cl-57">57</a>
<a href="#cl-58">58</a>
<a href="#cl-59">59</a>
<a href="#cl-60">60</a>
</pre></div></td><td class="code"><div class="highlight"><pre><a name="cl-1"></a><span class="cm">/*</span>
<a name="cl-2"></a><span class="cm"> *</span>
<a name="cl-3"></a><span class="cm"> * Insert meaningful comments here..</span>
<a name="cl-4"></a><span class="cm"> *</span>
<a name="cl-5"></a><span class="cm"> */</span>
<a name="cl-6"></a>
<a name="cl-7"></a><span class="kd">var</span> <span class="nx">version</span> <span class="o">=</span> <span class="mf">0.01</span><span class="p">;</span>
<a name="cl-8"></a><span class="kd">var</span> <span class="nx">intvl_id</span> <span class="o">=</span> <span class="kc">null</span><span class="p">;</span>
<a name="cl-9"></a><span class="kd">var</span> <span class="nx">count</span> <span class="o">=</span> <span class="mi">0</span><span class="p">;</span>
<a name="cl-10"></a><span class="kd">var</span> <span class="nx">started</span> <span class="o">=</span> <span class="kc">false</span><span class="p">;</span>
<a name="cl-11"></a>
<a name="cl-12"></a><span class="nx">jQuery</span><span class="p">.</span><span class="nx">loadanim</span> <span class="o">=</span> <span class="p">{</span>
<a name="cl-13"></a>
<a name="cl-14"></a>    <span class="nx">start</span> <span class="o">:</span> <span class="kd">function</span> <span class="p">(</span><span class="nx">options</span><span class="p">)</span> <span class="p">{</span>
<a name="cl-15"></a>        <span class="kd">var</span> <span class="nx">defaults</span> <span class="o">=</span> <span class="p">{</span>  
<a name="cl-16"></a>            <span class="nx">updateTime</span><span class="o">:</span> <span class="mi">400</span><span class="p">,</span>  <span class="c1">// milliseconds</span>
<a name="cl-17"></a>            <span class="nx">message</span><span class="o">:</span> <span class="s2">&quot;Loading&quot;</span><span class="p">,</span>
<a name="cl-18"></a>            <span class="nx">ellipsisText</span><span class="o">:</span> <span class="s2">&quot;...&quot;</span>  
<a name="cl-19"></a>        <span class="p">};</span>  
<a name="cl-20"></a>        <span class="kd">var</span> <span class="nx">options</span> <span class="o">=</span> <span class="nx">$</span><span class="p">.</span><span class="nx">extend</span><span class="p">(</span><span class="nx">defaults</span><span class="p">,</span> <span class="nx">options</span><span class="p">);</span>  
<a name="cl-21"></a>
<a name="cl-22"></a>        <span class="k">if</span> <span class="p">(</span><span class="nx">started</span><span class="p">)</span> <span class="p">{</span>
<a name="cl-23"></a>            <span class="k">return</span><span class="p">;</span>
<a name="cl-24"></a>        <span class="p">}</span>
<a name="cl-25"></a>        <span class="nx">$</span><span class="p">(</span><span class="s2">&quot;body&quot;</span><span class="p">).</span><span class="nx">append</span><span class="p">(</span><span class="s1">&#39;&lt;div id=&quot;loadAnim&quot;&gt;&lt;/div&gt;&#39;</span><span class="p">);</span>
<a name="cl-26"></a>        <span class="kd">var</span> <span class="nx">obj</span> <span class="o">=</span> <span class="nx">$</span><span class="p">(</span><span class="s2">&quot;div#loadAnim&quot;</span><span class="p">);</span>
<a name="cl-27"></a>        <span class="nx">obj</span><span class="p">.</span><span class="nx">css</span><span class="p">(</span><span class="s2">&quot;display&quot;</span><span class="p">,</span> <span class="s2">&quot;none&quot;</span><span class="p">);</span>
<a name="cl-28"></a>        <span class="nx">obj</span><span class="p">.</span><span class="nx">css</span><span class="p">(</span><span class="s2">&quot;color&quot;</span><span class="p">,</span> <span class="s2">&quot;#000&quot;</span><span class="p">);</span>
<a name="cl-29"></a>        <span class="nx">obj</span><span class="p">.</span><span class="nx">css</span><span class="p">(</span><span class="s2">&quot;background-color&quot;</span><span class="p">,</span> <span class="s2">&quot;#FEB&quot;</span><span class="p">);</span>
<a name="cl-30"></a>        <span class="nx">obj</span><span class="p">.</span><span class="nx">css</span><span class="p">(</span><span class="s2">&quot;position&quot;</span><span class="p">,</span> <span class="s2">&quot;absolute&quot;</span><span class="p">);</span>
<a name="cl-31"></a>        <span class="nx">obj</span><span class="p">.</span><span class="nx">css</span><span class="p">(</span><span class="s2">&quot;width&quot;</span><span class="p">,</span> <span class="p">(</span><span class="nx">options</span><span class="p">.</span><span class="nx">message</span><span class="p">.</span><span class="nx">length</span> <span class="o">+</span> <span class="nx">options</span><span class="p">.</span><span class="nx">ellipsisText</span><span class="p">.</span><span class="nx">length</span> <span class="o">+</span> <span class="mi">1</span><span class="p">)</span> <span class="o">+</span> <span class="s2">&quot;ex&quot;</span><span class="p">);</span>
<a name="cl-32"></a>        <span class="nx">obj</span><span class="p">.</span><span class="nx">css</span><span class="p">(</span><span class="s2">&quot;padding&quot;</span><span class="p">,</span> <span class="s2">&quot;1ex&quot;</span><span class="p">);</span>
<a name="cl-33"></a>        <span class="nx">obj</span><span class="p">.</span><span class="nx">css</span><span class="p">(</span><span class="s2">&quot;left&quot;</span><span class="p">,</span> <span class="s2">&quot;49%&quot;</span><span class="p">);</span>
<a name="cl-34"></a>        <span class="nx">obj</span><span class="p">.</span><span class="nx">css</span><span class="p">(</span><span class="s2">&quot;top&quot;</span><span class="p">,</span> <span class="s2">&quot;0&quot;</span><span class="p">);</span>
<a name="cl-35"></a>        <span class="nx">obj</span><span class="p">.</span><span class="nx">css</span><span class="p">(</span><span class="s2">&quot;z-index&quot;</span><span class="p">,</span> <span class="s2">&quot;9999&quot;</span><span class="p">);</span>
<a name="cl-36"></a>        <span class="nx">started</span> <span class="o">=</span> <span class="kc">true</span><span class="p">;</span>
<a name="cl-37"></a>        <span class="nx">obj</span><span class="p">.</span><span class="nx">html</span><span class="p">(</span><span class="nx">options</span><span class="p">.</span><span class="nx">message</span><span class="p">);</span>
<a name="cl-38"></a>        <span class="nx">count</span> <span class="o">=</span> <span class="mi">0</span><span class="p">;</span>
<a name="cl-39"></a>        <span class="nx">intvl_id</span> <span class="o">=</span>  <span class="nx">setInterval</span><span class="p">(</span><span class="kd">function</span> <span class="p">()</span> <span class="p">{</span>
<a name="cl-40"></a>            <span class="k">if</span> <span class="p">(</span><span class="o">++</span><span class="nx">count</span> <span class="o">&gt;</span> <span class="nx">options</span><span class="p">.</span><span class="nx">ellipsisText</span><span class="p">.</span><span class="nx">length</span><span class="p">)</span> <span class="p">{</span>
<a name="cl-41"></a>                <span class="nx">count</span> <span class="o">=</span> <span class="mi">0</span><span class="p">;</span>
<a name="cl-42"></a>            <span class="p">}</span>
<a name="cl-43"></a>            <span class="kd">var</span> <span class="nx">obj</span> <span class="o">=</span> <span class="nx">$</span><span class="p">(</span><span class="s2">&quot;div#loadAnim&quot;</span><span class="p">);</span>
<a name="cl-44"></a>            <span class="nx">obj</span><span class="p">.</span><span class="nx">html</span><span class="p">(</span><span class="nx">options</span><span class="p">.</span><span class="nx">message</span> <span class="o">+</span> <span class="nx">options</span><span class="p">.</span><span class="nx">ellipsisText</span><span class="p">.</span><span class="nx">substr</span><span class="p">(</span><span class="mi">0</span><span class="p">,</span> <span class="nx">count</span><span class="p">));</span>
<a name="cl-45"></a>          <span class="p">},</span> <span class="nx">options</span><span class="p">.</span><span class="nx">updateTime</span><span class="p">);</span>
<a name="cl-46"></a>        <span class="nx">obj</span><span class="p">.</span><span class="nx">css</span><span class="p">(</span><span class="s2">&quot;display&quot;</span><span class="p">,</span> <span class="s2">&quot;block&quot;</span><span class="p">);</span>
<a name="cl-47"></a>    <span class="p">},</span>
<a name="cl-48"></a>    <span class="nx">stop</span> <span class="o">:</span> <span class="kd">function</span> <span class="p">(</span><span class="nx">options</span><span class="p">)</span> <span class="p">{</span>
<a name="cl-49"></a>        <span class="k">if</span> <span class="p">(</span><span class="o">!</span><span class="nx">started</span><span class="p">)</span> <span class="p">{</span>
<a name="cl-50"></a>            <span class="k">return</span><span class="p">;</span>
<a name="cl-51"></a>        <span class="p">}</span>
<a name="cl-52"></a>        <span class="nx">started</span> <span class="o">=</span> <span class="kc">false</span><span class="p">;</span>
<a name="cl-53"></a>        <span class="nx">clearInterval</span><span class="p">(</span><span class="nx">intvl_id</span><span class="p">);</span>
<a name="cl-54"></a>        <span class="nx">intvl_id</span> <span class="o">=</span> <span class="kc">null</span><span class="p">;</span>
<a name="cl-55"></a>        <span class="kd">var</span> <span class="nx">obj</span> <span class="o">=</span> <span class="nx">$</span><span class="p">(</span><span class="s2">&quot;div#loadAnim&quot;</span><span class="p">);</span>
<a name="cl-56"></a>        <span class="nx">obj</span><span class="p">.</span><span class="nx">css</span><span class="p">(</span><span class="s2">&quot;display&quot;</span><span class="p">,</span> <span class="s2">&quot;none&quot;</span><span class="p">);</span>
<a name="cl-57"></a>        <span class="nx">obj</span><span class="p">.</span><span class="nx">remove</span><span class="p">();</span>
<a name="cl-58"></a>    <span class="p">}</span>
<a name="cl-59"></a>
<a name="cl-60"></a><span class="p">};</span>
</pre></div>
</td></tr></table>
    </div>
  
  </div>
  


  <div id="mask"><div></div></div>

  </div>

      </div>
    </div>

  </div>

  <div id="footer">
    <ul id="footer-nav">
      <li>Copyright © 2012 <a href="http://atlassian.com">Atlassian</a></li>
      <li><a href="http://www.atlassian.com/hosted/terms.jsp">Terms of Service</a></li>
      <li><a href="http://www.atlassian.com/about/privacy.jsp">Privacy</a></li>
      <li><a href="//bitbucket.org/site/master/issues/new">Report a Bug to Bitbucket</a></li>
      <li><a href="http://confluence.atlassian.com/x/IYBGDQ">API</a></li>
      <li><a href="http://status.bitbucket.org/">Server Status</a></li>
    </ul>
    <ul id="social-nav">
      <li class="blog"><a href="http://blog.bitbucket.org">Bitbucket Blog</a></li>
      <li class="twitter"><a href="http://www.twitter.com/bitbucket">Twitter</a></li>
    </ul>
    <h5>We run</h5>
    <ul id="technologies">
      <li><a href="http://www.djangoproject.com/">Django 1.3.1</a></li>
      <li><a href="//bitbucket.org/jespern/django-piston/">Piston 0.3dev</a></li>
      <li><a href="http://git-scm.com/">Git 1.7.6</a></li>
      <li><a href="http://www.selenic.com/mercurial/">Hg 1.9.1</a></li>
      <li><a href="http://www.python.org">Python 2.7.2</a></li>
      <li>d050823bec1a | bitbucket01</li>
    </ul>
  </div>

  <script src="https://dwz7u9t8u8usb.cloudfront.net/m/22e5034559c2/js/lib/global.js"></script>






  <script>
    BB.gaqPush(['_trackPageview']);
  
    BB.gaqPush(['atl._trackPageview']);

    

    

    (function () {
        var ga = document.createElement('script');
        ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
        ga.setAttribute('async', 'true');
        document.documentElement.firstChild.appendChild(ga);
    }());
  </script>

</body>
</html>
