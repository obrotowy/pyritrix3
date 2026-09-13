from lxml import etree
from io import BytesIO


class config():
    def __init__(self):
        pass

    @staticmethod
    def generate(overrides: dict, output_path=None) -> BytesIO:
        parser = etree.XMLParser(remove_blank_text=False)
        root = etree.fromstring(_CFG_TEMPLATE.strip().encode("UTF-8"), parser)
        tree = etree.ElementTree(root)

        bean = root.find(f".//{{{NS}}}bean[@id='simpleOverrides']")
        value_el = bean.find(
            f".//{{{NS}}}property[@name='properties']/{{{NS}}}value")

        lines = [f"{key}={val}" for key, val in overrides.items()]
        value_el.text = "\n".join(lines)
        output = BytesIO()
        tree.write(output, encoding="UTF-8", xml_declaration=True)
        if output_path:
            tree.write(output_path, encoding="UTF-8", xml_declaration=True)
        output.seek(0)
        return output


NS = "http://www.springframework.org/schema/beans"

_CFG_TEMPLATE = """
<?xml version="1.0" encoding="UTF-8"?>
<!-- Heritrix 3 crawl job configuration -->
<beans xmlns="http://www.springframework.org/schema/beans"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xmlns:context="http://www.springframework.org/schema/context"
        xmlns:aop="http://www.springframework.org/schema/aop"
        xmlns:tx="http://www.springframework.org/schema/tx"
        xsi:schemaLocation="http://www.springframework.org/schema/beans http://www.springframework.org/schema/beans/spring-beans-3.0.xsd
           http://www.springframework.org/schema/aop http://www.springframework.org/schema/aop/spring-aop-3.0.xsd
           http://www.springframework.org/schema/tx http://www.springframework.org/schema/tx/spring-tx-3.0.xsd
           http://www.springframework.org/schema/context http://www.springframework.org/schema/context/spring-context-3.0.xsd">

 <context:annotation-config/>

 <!-- Overrides: values here replace matching bean properties elsewhere in this file. -->
 <bean id="simpleOverrides" class="org.springframework.beans.factory.config.PropertyOverrideConfigurer">
  <property name="properties">
   <value>
   </value>
  </property>
 </bean>

 <!-- Crawl metadata: identification of crawler/operator -->
 <bean id="metadata" class="org.archive.modules.CrawlMetadata" autowire="byName">
  <property name="operatorContactUrl" value="https://eti.pg.edu.pl/"/>
  <property name="jobName" value="DTN-WEB-BROWSER"/>
  <property name="description" value="asdfdsfaafsd"/>
 </bean>

 <!-- Seeds: crawl starting points -->
 <bean id="seeds" class="org.archive.modules.seeds.TextSeedModule">
  <property name="textSource">
   <bean class="org.archive.spring.ConfigString">
    <property name="value">
     <value>
# [see override above]
     </value>
    </property>
   </bean>
  </property>
 </bean>

 <bean id="acceptSurts" class="org.archive.modules.deciderules.surt.SurtPrefixedDecideRule">
 </bean>

 <!-- Scope: rules for which discovered URIs to crawl.
      Order matters: the last decision returned other than 'NONE' wins. -->
 <bean id="scope" class="org.archive.modules.deciderules.DecideRuleSequence">
  <property name="rules">
   <list>
    <!-- reject everything by default -->
    <bean class="org.archive.modules.deciderules.RejectDecideRule" />
    <!-- accept URIs within configured/seed-implied SURT prefixes -->
    <ref bean="acceptSurts" />
    <!-- reject URIs beyond the configured link-hop-count from seeds -->
    <bean class="org.archive.modules.deciderules.TooManyHopsDecideRule" />
    <!-- accept URIs beyond the hop-count limit if they were transcluded (e.g. embeds) -->
    <bean class="org.archive.modules.deciderules.TransclusionDecideRule" />
    <!-- reject URIs matching a configurable (initially empty) set of REJECT SURTs -->
    <bean class="org.archive.modules.deciderules.surt.SurtPrefixedDecideRule">
     <property name="decision" value="REJECT"/>
     <property name="seedsAsSurtPrefixes" value="false"/>
     <property name="surtsDumpFile" value="${launchId}/negative-surts.dump" />
    </bean>
    <!-- reject URIs matching a configurable (initially empty) set of regexes -->
    <bean class="org.archive.modules.deciderules.MatchesListRegexDecideRule">
     <property name="decision" value="REJECT"/>
    </bean>
    <!-- reject URIs with suspicious repeating path segments -->
    <bean class="org.archive.modules.deciderules.PathologicalPathDecideRule" />
    <!-- reject URIs with too many path segments -->
    <bean class="org.archive.modules.deciderules.TooManyPathSegmentsDecideRule" />
    <!-- always accept URIs marked as a prerequisite for another URI -->
    <bean class="org.archive.modules.deciderules.PrerequisiteAcceptDecideRule" />
    <!-- always reject unsupported URI schemes -->
    <bean class="org.archive.modules.deciderules.SchemeNotInSetDecideRule" />
   </list>
  </property>
 </bean>

 <!-- Processing chains: CandidateChain (before enqueue), FetchChain (on collection),
      DispositionChain (after fetch/link-extraction). -->

 <!-- Candidate chain -->
 <bean id="candidateScoper" class="org.archive.crawler.prefetch.CandidateScoper" />
 <bean id="preparer" class="org.archive.crawler.prefetch.FrontierPreparer" />
 <bean id="candidateProcessors" class="org.archive.modules.CandidateChain">
  <property name="processors">
   <list>
    <ref bean="candidateScoper"/>
    <ref bean="preparer"/>
   </list>
  </property>
 </bean>

 <!-- Fetch chain -->
 <bean id="preselector" class="org.archive.crawler.prefetch.Preselector" />
 <bean id="preconditions" class="org.archive.crawler.prefetch.PreconditionEnforcer" />
 <bean id="fetchDns" class="org.archive.modules.fetcher.FetchDNS" />
 <bean id="fetchHttp" class="org.archive.modules.fetcher.FetchHTTP" />
 <bean id="extractorHttp" class="org.archive.modules.extractor.ExtractorHTTP" />
 <bean id="extractorRobotsTxt" class="org.archive.modules.extractor.ExtractorRobotsTxt" />
 <bean id="extractorSitemap" class="org.archive.modules.extractor.ExtractorSitemap" />
 <bean id="extractorHtml" class="org.archive.modules.extractor.ExtractorHTML" />
 <bean id="extractorCss" class="org.archive.modules.extractor.ExtractorCSS" />
 <bean id="extractorJs" class="org.archive.modules.extractor.ExtractorJS" />
 <bean id="extractorSwf" class="org.archive.modules.extractor.ExtractorSWF" />
 <bean id="fetchProcessors" class="org.archive.modules.FetchChain">
  <property name="processors">
   <list>
    <ref bean="preselector"/>
    <ref bean="preconditions"/>
    <ref bean="fetchDns"/>
    <ref bean="fetchHttp"/>
    <ref bean="extractorHttp"/>
    <ref bean="extractorRobotsTxt"/>
    <ref bean="extractorSitemap"/>
    <ref bean="extractorHtml"/>
    <ref bean="extractorCss"/>
    <ref bean="extractorJs"/>
    <ref bean="extractorSwf"/>
   </list>
  </property>
 </bean>

 <!-- Disposition chain -->
 <bean id="warcWriter" class="org.archive.modules.writer.WARCWriterChainProcessor" />
 <bean id="candidates" class="org.archive.crawler.postprocessor.CandidatesProcessor" />
 <bean id="disposition" class="org.archive.crawler.postprocessor.DispositionProcessor" />
 <bean id="dispositionProcessors" class="org.archive.modules.DispositionChain">
  <property name="processors">
   <list>
    <ref bean="warcWriter"/>
    <ref bean="candidates"/>
    <ref bean="disposition"/>
   </list>
  </property>
 </bean>

 <!-- Crawl controller: control interface, unifying context -->
 <bean id="crawlController" class="org.archive.crawler.framework.CrawlController" />

 <!-- Frontier: record of all URIs discovered and queued for collection -->
 <bean id="frontier" class="org.archive.crawler.frontier.BdbFrontier" />

 <!-- URI uniq filter: used by the frontier to remember already-seen URIs -->
 <bean id="uriUniqFilter" class="org.archive.crawler.util.BdbUriUniqFilter" />

 <!-- Example overlay sheets: adjust queue behavior for URIs matched via a
      SheetAssociation (e.g. SurtPrefixesSheetAssociation, not configured by default). -->
 <bean id='forceRetire' class='org.archive.spring.Sheet'>
  <property name='map'>
   <map>
    <entry key='disposition.forceRetire' value='true'/>
   </map>
  </property>
 </bean>

 <bean id='smallBudget' class='org.archive.spring.Sheet'>
  <property name='map'>
   <map>
    <entry key='frontier.balanceReplenishAmount' value='20'/>
    <entry key='frontier.queueTotalBudget' value='100'/>
   </map>
  </property>
 </bean>

 <bean id='veryPolite' class='org.archive.spring.Sheet'>
  <property name='map'>
   <map>
    <entry key='disposition.delayFactor' value='10'/>
    <entry key='disposition.minDelayMs' value='10000'/>
    <entry key='disposition.maxDelayMs' value='1000000'/>
    <entry key='disposition.respectCrawlDelayUpToSeconds' value='3600'/>
   </map>
  </property>
 </bean>

 <bean id='highPrecedence' class='org.archive.spring.Sheet'>
  <property name='map'>
   <map>
    <entry key='frontier.balanceReplenishAmount' value='20'/>
    <entry key='frontier.queueTotalBudget' value='100'/>
   </map>
  </property>
 </bean>

 <!-- Action directory: watches a disk directory for mid-crawl operations
      (new URIs, scripts, etc.) -->
 <bean id="actionDirectory" class="org.archive.crawler.framework.ActionDirectory" />

 <!-- Crawl limit enforcer: stops the crawl once configured limits are reached -->
 <bean id="crawlLimiter" class="org.archive.crawler.framework.CrawlLimitEnforcer">
     <property name="maxBytesDownload" value="0" />
     <property name="maxDocumentsDownload" value="0" />
     <property name="maxTimeSeconds" value="0" />
 </bean>

 <!-- Checkpoint service -->
 <bean id="checkpointService" class="org.archive.crawler.framework.CheckpointService" />

 <!-- Statistics tracker: stats/reporting collector -->
 <bean id="statisticsTracker" class="org.archive.crawler.reporting.StatisticsTracker" autowire="byName" />

 <!-- Crawler logger module: shared logging facility -->
 <bean id="loggerModule" class="org.archive.crawler.reporting.CrawlerLoggerModule" />

 <!-- Sheet overlays manager: applies contextual overlay Sheets to matching URIs -->
 <bean id="sheetOverlaysManager" autowire="byType" class="org.archive.crawler.spring.SheetOverlaysManager" />

 <!-- BDB module: shared BDB-JE disk persistence manager -->
 <bean id="bdb" class="org.archive.bdb.BdbModule" />

 <!-- BDB cookie store: disk-based cookie storage for FetchHTTP -->
 <bean id="cookieStore" class="org.archive.modules.fetcher.BdbCookieStore" />

 <!-- Server cache: shared cache of server/host info -->
 <bean id="serverCache" class="org.archive.modules.net.BdbServerCache" />

 <!-- Config path configurer: makes crawl paths relative to this file,
      and tracks crawl files for the web UI -->
 <bean id="configPathConfigurer" class="org.archive.spring.ConfigPathConfigurer" />

</beans>
"""
